// +------------------------------------------------------------------+
// |             ____ _               _        __  __ _  __           |
// |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
// |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
// |           | |___| | | |  __/ (__|   <    | |  | | . \            |
// |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
// |                                                                  |
// | Copyright Mathias Kettner 2015             mk@mathias-kettner.de |
// +------------------------------------------------------------------+
//
// This file is part of Check_MK.
// The official homepage is at http://mathias-kettner.de/check_mk.
//
// check_mk is free software;  you can redistribute it and/or modify it
// under the  terms of the  GNU General Public License  as published by
// the Free Software Foundation in version 2.  check_mk is  distributed
// in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
// out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
// PARTICULAR PURPOSE. See the  GNU General Public License for more de-
// ails.  You should have  received  a copy of the  GNU  General Public
// License along with GNU Make; see the file  COPYING.  If  not,  write
// to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
// Boston, MA 02110-1301 USA.


#include "wmiHelper.h"
#include "stringutil.h"
#include <comdef.h>
#include <oleauto.h>
#include <ios>
#include <sstream>
#include <iostream>


using namespace wmi;
using namespace std;


std::string ComException::resolveError(HRESULT result)
{
    switch (static_cast<ULONG>(result)) {
        case WBEM_E_INVALID_NAMESPACE:  return "Invalid Namespace";
        case WBEM_E_ACCESS_DENIED:      return "Access Denied";
        case WBEM_E_INVALID_CLASS:      return "Invalid Class";
        case WBEM_E_INVALID_QUERY:      return "Invalid Query";
        default:  return to_utf8(_com_error(result, getErrorInfo()).ErrorMessage());
    }
}


ComException::ComException(const string &message, HRESULT result)
    : runtime_error(message + ": " + resolveError(result)  + " (" + toStringHex(result) + ")")
{
}


ComTypeException::ComTypeException(const string &message)
    : runtime_error(message)
{
}


IErrorInfo *ComException::getErrorInfo()
{
    IErrorInfo *result;
    GetErrorInfo(0, &result);
    return result;
}


string ComException::toStringHex(HRESULT res)
{
    ostringstream out;
    out << hex << res;
    return out.str();
}


Variant::Variant(const VARIANT &val)
    : _value(val)
{
}


Variant::~Variant()
{
    VariantClear(&_value);
}


void releaseInterface(IUnknown *ptr)
{
    if (ptr != NULL) {
        ptr->Release();
    }
}


ObjectWrapper::ObjectWrapper(IWbemClassObject *object)
    : _current(object, releaseInterface)
{
}


ObjectWrapper::ObjectWrapper(const ObjectWrapper &reference)
    : _current(reference._current)
{
}


bool ObjectWrapper::contains(const wchar_t *key) const
{
    VARIANT value;
    HRESULT res = _current->Get(key, 0, &value, NULL, NULL);
    if (FAILED(res)) {
        return false;
    }
    bool not_null = value.vt != VT_NULL;
    VariantClear(&value);
    return not_null;
}

int ObjectWrapper::typeId(const wchar_t *key) const
{
    VARIANT value;
    HRESULT res = _current->Get(key, 0, &value, NULL, NULL);
    if (FAILED(res)) {
        return 0;
    }
    int type_id = value.vt;
    VariantClear(&value);
    return type_id;

}

ObjectWrapper::~ObjectWrapper()
{
}


VARIANT ObjectWrapper::getVarByKey(const wchar_t *key) const
{
    VARIANT value;
    HRESULT res = _current->Get(key, 0, &value, NULL, NULL);
    if (FAILED(res)) {
        throw ComException("Failed to retrieve key: " + to_utf8(key), res);
    }

    return value;
}


Result::Result()
    : ObjectWrapper(NULL)
    , _enumerator(NULL, releaseInterface)
{
}


Result::Result(const Result &reference)
    : ObjectWrapper(NULL)
    , _enumerator(reference._enumerator)
{
    next();
}


Result::Result(IEnumWbemClassObject *enumerator)
    : ObjectWrapper(NULL)
    , _enumerator(enumerator, releaseInterface)
{
    next();
}


Result::~Result()
{
}


Result &Result::operator=(const Result &reference)
{
    if (&reference != this) {
        if (_enumerator != NULL) {
            _enumerator->Release();
        }
        _enumerator = reference._enumerator;
        next();
    }
    return *this;
}


bool Result::valid() const
{
    return _current.get() != NULL;
}


vector<wstring> Result::names() const
{
    vector<wstring> result;
    SAFEARRAY *names = NULL;
    HRESULT res = _current->GetNames(
            NULL,
            WBEM_FLAG_ALWAYS | WBEM_FLAG_NONSYSTEM_ONLY,
            NULL,
            &names);

    if (FAILED(res)) {
        throw ComException("Failed to retrieve field names", res);
    }

    long lLower, lUpper;
    BSTR propName = NULL;
    SafeArrayGetLBound(names, 1, &lLower);
    SafeArrayGetUBound(names, 1, &lUpper);

    for (long i = lLower; i <= lUpper; ++i) {
        res = SafeArrayGetElement(names, &i, &propName);
        result.push_back(wstring(propName));
        SysFreeString(propName);
    }

    SafeArrayDestroy(names);
    return result;
}


bool Result::next()
{
    if (_enumerator == NULL) {
        return false;
    }

    IWbemClassObject *obj;
    ULONG numReturned;
    // always retrieve only one element
    HRESULT res = _enumerator->Next(WBEM_INFINITE, 1, &obj, &numReturned);

    if (FAILED(res)) {
        // in this case the "current" object isn't changed to guarantee that the
        // Result remains valid
        throw ComException("Failed to retrieve element", res);
    }

    if (numReturned == 0) {
        // no more values. the current object remains at the last element so that
        // a call to get continues to work
        return false;
    }

    _current.reset(obj, releaseInterface);
    return true;
}


template <> int Variant::get()
{
    switch (_value.vt) {
        case VT_I1: return _value.bVal;
        case VT_I2: return _value.iVal;
        case VT_I4: return _value.intVal;
        case VT_UI1: return _value.cVal;
        case VT_UI2: return _value.uiVal;
        case VT_UI4: return _value.intVal;
        default: throw ComTypeException(string("wrong value type requested: ") + to_string(_value.vt));
    }
}


template <> bool Variant::get()
{
    switch (_value.vt) {
        case VT_BOOL: return _value.boolVal;
        default: throw ComTypeException(string("wrong value type requested: ") + to_string(_value.vt));
    }
}


template <> ULONG Variant::get()
{
    switch (_value.vt) {
        case VT_UI1: return _value.cVal;
        case VT_UI2: return _value.uiVal;
        case VT_UI4: return _value.ulVal;
        default: throw ComTypeException(string("wrong value type requested: ") + to_string(_value.vt));
    }
}


template <> ULONGLONG Variant::get()
{
    switch (_value.vt) {
        case VT_UI8: return _value.ullVal;
        default: throw ComTypeException(string("wrong value type requested: ") + to_string(_value.vt));
    }
}


template <> string Variant::get()
{
    switch (_value.vt) {
        case VT_BSTR: return to_utf8(_value.bstrVal);
        default: throw ComTypeException(string("wrong value type requested: ") + to_string(_value.vt));
    }
}


template <> wstring Variant::get()
{
    if (_value.vt & VT_ARRAY) {
        return L"<array>";
    }
    if (_value.vt & VT_VECTOR) {
        return L"<vector>";
    }

    switch (_value.vt) {
        case VT_BSTR:
            return wstring(_value.bstrVal);
        case VT_I1:
        case VT_I2:
        case VT_I4:
        case VT_UI1:
        case VT_UI2:
        case VT_UI4:
            return std::to_wstring(get<int>());
        case VT_UI8:
            return std::to_wstring(get<ULONGLONG>());
        case VT_BOOL:
            return std::to_wstring(get<bool>());
        case VT_NULL:
            return L"";
        default:
            throw ComTypeException(string("wrong value type requested: ") + to_string(_value.vt));
    }
}


class COMManager {
public:
    static void init() {
        // this is apparently thread safe in C++11 and in gcc even before that
        // see §6.4 in C++11 standard or §6.7 in C++14
        static COMManager s_Instance;
    }

    ~COMManager() {
        CoUninitialize();
    }
private:
    COMManager() {
        HRESULT res = CoInitializeEx(0, COINIT_MULTITHREADED);
        if (FAILED(res)) {
            throw ComException("Failed to initialize COM", res);
        }

        res = CoInitializeSecurity(
                NULL,                        // security descriptor
                -1,                          // authentication
                NULL,                        // authentication services
                NULL,                        // reserved
                RPC_C_AUTHN_LEVEL_DEFAULT,   // authentication level
                RPC_C_IMP_LEVEL_IMPERSONATE, // impersonation level
                NULL,                        // authentication info
                EOAC_NONE,                   // additional capabilities
                NULL                         // reserved
                );
        if (FAILED(res)) {
            throw ComException("Failed to initialize COM security", res);
        }
    }
private:
};


Helper::Helper(LPCWSTR path)
    : _locator(NULL)
    , _path(path)
{
    COMManager::init();

    _locator = getWBEMLocator();
    _services = connectServer(_locator);
}


Helper::~Helper()
{
    if (_locator != NULL) {
        _locator->Release();
    }
    if (_services != NULL) {
        _services->Release();
    }
}


IWbemLocator *Helper::getWBEMLocator()
{
    IWbemLocator *locator = NULL;

    HRESULT res = CoCreateInstance(
            CLSID_WbemLocator,
            0,
            CLSCTX_INPROC_SERVER,
            IID_IWbemLocator, (LPVOID *) &locator);

    if (FAILED(res)) {
        throw ComException("Failed to create locator object", res);
    }
    return locator;
}


IWbemServices *Helper::connectServer(IWbemLocator *locator)
{
    IWbemServices *services = NULL;

    HRESULT res = locator->ConnectServer(
         _bstr_t(_path.c_str()),  // WMI path
         NULL,                    // user name
         NULL,                    // user password
         0,                       // locale
         0,                       // security flags
         0,                       // authority
         0,                       // context object
         &services                // services proxy
         );

    if (FAILED(res)) {
        throw ComException("Failed to connect", res);
    }
    return services;
}


void Helper::setProxyBlanket(IWbemServices *services)
{
    HRESULT res = CoSetProxyBlanket(
       services,                    // the proxy to set
       RPC_C_AUTHN_WINNT,           // authentication service
       RPC_C_AUTHZ_NONE,            // authorization service
       NULL,                        // server principal name
       RPC_C_AUTHN_LEVEL_CALL,      // authentication level
       RPC_C_IMP_LEVEL_IMPERSONATE, // impersonation level
       NULL,                        // client identity
       EOAC_NONE                    // proxy capabilities
    );

    if (FAILED(res)) {
        throw ComException("Failed to set proxy blanket", res);
    }
}


Result Helper::query(LPCWSTR query)
{
    IEnumWbemClassObject *enumerator = NULL;
    // WBEM_FLAG_RETURN_IMMEDIATELY makes the call semi-synchronous which means we can
    // return to caller immediately, iterating the result may break until data is available.
    // WBEM_FLAG_FORWARD_ONLY allows wmi to free the memory of results already iterated,
    // thus reducing memory usage
    HRESULT res = _services->ExecQuery(_bstr_t(L"WQL"), _bstr_t(query),
                                       WBEM_FLAG_FORWARD_ONLY | WBEM_FLAG_RETURN_IMMEDIATELY,
                                       NULL, &enumerator);

    if (FAILED(res)) {
        throw ComException(string("Failed to execute query \"") + to_utf8(query) + "\"", res);
    }
    return Result(enumerator);
}


ObjectWrapper Helper::call(ObjectWrapper &result, LPCWSTR method)
{
    // NOTE: currently broken and unused, only here as a starting point for future implementation
    IWbemClassObject* outParams = NULL;

    BSTR className;
    HRESULT res = result._current->GetMethodOrigin(method, &className);
    if (FAILED(res)) {
        throw ComException(string("Failed to determine method origin: ") + to_utf8(method), res);
    }

    // please don't ask me why ExecMethod needs the method name in a writable
    // buffer...
    BSTR methodName = SysAllocString(method);

    res = _services->ExecMethod(className, methodName, 0,
                                NULL, result._current.get(), &outParams, NULL);

    SysFreeString(methodName);

    return ObjectWrapper(outParams);
}

