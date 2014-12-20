import sys
from ctypes import *
from ctypes.util import find_library
import time

iokit = CDLL(find_library('IOKit'))
foundation = CDLL(find_library('Foundation'))
application_services = CDLL(find_library('ApplicationServices'))
coregraphics = CDLL(find_library('CoreGraphics'))


# kNilOptions = IOOptionBits(0)
kNilOptions = 0
kCFStringEncodingASCII = 0x0600
kCFStringEncodingUTF8 = 0x08000100
kIODisplayBrightnessKey = "brightness"
kIOReturnSuccess = 0


# void CFRelease(CFTypeRef cf);
CFRelease = foundation.CFRelease
CFRelease.restype = None
CFRelease.argtypes = (c_void_p,)


# CFStringRef CFStringCreateWithBytes(CFAllocatorRef alloc, const UInt8 *bytes, CFIndex numBytes, CFStringEncoding encoding, Boolean isExternalRepresentation );
CFStringCreateWithBytes = foundation.CFStringCreateWithBytes
CFStringCreateWithBytes.restype = c_void_p
CFStringCreateWithBytes.argtypes = (c_void_p, c_char_p, c_long, c_uint32, c_int,)


# IOReturn IODisplaySetFloatParameter(io_service_t service, IOOptionBits options, CFStringRef parameterName, float value);
IODisplaySetFloatParameter = iokit.IODisplaySetFloatParameter
IODisplaySetFloatParameter.restype = c_int
IODisplaySetFloatParameter.argtypes = (c_void_p, c_uint32, c_void_p, c_float,)


# IOReturn IODisplayGetFloatParameter(io_service_t service, IOOptionBits options, CFStringRef parameterName, float *value);
IODisplayGetFloatParameter = iokit.IODisplayGetFloatParameter
IODisplayGetFloatParameter.restype = c_int
IODisplayGetFloatParameter.argtypes = (c_void_p, c_uint32, c_void_p, POINTER(c_float),)


# CGDirectDisplayID CGMainDisplayID(void);
CGMainDisplayID = coregraphics.CGMainDisplayID
CGMainDisplayID.restype = c_uint32
CGMainDisplayID.argtypes = ()


# io_service_t CGDisplayIOServicePort(CGDirectDisplayID display);
CGDisplayIOServicePort = coregraphics.CGDisplayIOServicePort
CGDisplayIOServicePort.restype = c_void_p
CGDisplayIOServicePort.argtypes = (c_uint32,)


def set_brightness(brightness):
    targetDisplay = CGMainDisplayID()
    service = CGDisplayIOServicePort(targetDisplay)

    key = CFStringCreateWithBytes(0, kIODisplayBrightnessKey, len(kIODisplayBrightnessKey), kCFStringEncodingASCII, 0)
    try:
        dErr = IODisplaySetFloatParameter(service, kNilOptions, key, brightness)
        if dErr != kIOReturnSuccess:
            raise RuntimeError("IODisplaySetFloatParameter failed with error 0x%x" % dErr)
    finally:
        CFRelease(key)

def get_brightness():
    targetDisplay = CGMainDisplayID()
    service = CGDisplayIOServicePort(targetDisplay)

    key = CFStringCreateWithBytes(0, kIODisplayBrightnessKey, len(kIODisplayBrightnessKey), kCFStringEncodingASCII, 0)
    try:
        brightness = c_float()
        dErr = IODisplayGetFloatParameter(service, kNilOptions, key, byref(brightness))
        if dErr != kIOReturnSuccess:
            raise RuntimeError("IODisplayGetFloatParameter failed: %r" % dErr)
        else:
            return brightness.value
    finally:
        CFRelease(key)


def flash():
    original_brightness = get_brightness()

    for i in range(3):
        set_brightness(1.0)
        time.sleep(0.1)
        set_brightness(0)
        time.sleep(1)

    set_brightness(original_brightness)


original_hook = sys.excepthook
def flash_on_exception(type, value, traceback):
    flash()
    if original_hook:
        original_hook(type, value, traceback)
sys.excepthook = flash_on_exception


def darken():
    brightness = get_brightness()
    while brightness > 0:
        brightness -= .1
        set_brightness(brightness)
        time.sleep(0.2)

def lighten(target_brightness):
    brightness = get_brightness()
    while brightness < target_brightness:
        brightness += .1
        set_brightness(brightness)
        time.sleep(0.4)


def warning():
    original_brightness = get_brightness()
    darken()
    flash()
    time.sleep(.8)
    lighten(original_brightness)
