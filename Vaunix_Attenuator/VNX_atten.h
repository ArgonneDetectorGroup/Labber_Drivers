
// --------------------------------- VNX_atten.h -------------------------------------------
//
//	Include file for LabBrick attenuator API
//
// (c) 2008 - 2016 by Vaunix Corporation, all rights reserved
//
//	RD Version 2.0	2/2014
//
//  RD 8-31-10 version for Microsoft C __cdecl calling convention
//
//	RD	This version supports the new Version 2 functions that can be used with attenuators
//		that have V2 level functionality.
//
//	RD 5-9-16 version adds parameterized calling convention

// --	these symbols are set to the calling convention of our ANSI, CPP, or STDCALL style DLLs
//		pick the one that corresponds to the DLL you are using, this parameter is set for each
//		style of SDK.
//
#define VNX_ANSI 1
#define VNX_CPP 0
#define VNX_STDCALL 0

#define VNX_ATTEN_API __declspec(dllimport)

#ifdef __cplusplus
  #if (VNX_ANSI || VNX_STDCALL)
  extern "C" {
  #endif
#endif

#if VNX_STDCALL
 #define VB6_API __stdcall
#else
 #define VB6_API 
#endif


// ----------- Global Equates ------------
#define MAXDEVICES 64
#define MAX_MODELNAME 32
#define PROFILE_MAX 100

// ----------- Data Types ----------------

#define DEVID unsigned int

// ----------- Mode Bit Masks ------------

#define MODE_RFON	0x00000040			// bit is 1 for RF on, 0 if RF is off
#define MODE_INTREF	0x00000020			// bit is 1 for internal osc., 0 for external reference
#define MODE_SWEEP	0x0000001F			// bottom 5 bits are used to keep the ramp control bits				


// ----------- Command Equates -----------


// Status returns for commands
#define LVSTATUS int

#define STATUS_OK 0
#define BAD_PARAMETER			0x80010000		// out of range input -- frequency outside min/max etc.
#define BAD_HID_IO				0x80020000		// a failure in the Windows I/O subsystem
#define DEVICE_NOT_READY		0x80030000		// device isn't open, no handle, etc.
#define FEATURE_NOT_SUPPORTED	0x80040000		// the selected Lab Brick does not support this function
												// Profiles and Bi-directional ramps are only supported in
												// LDA models manufactured after

// Status returns for DevStatus

#define INVALID_DEVID		0x80000000		// MSB is set if the device ID is invalid
#define DEV_CONNECTED		0x00000001		// LSB is set if a device is connected
#define DEV_OPENED			0x00000002		// set if the device is opened
#define SWP_ACTIVE			0x00000004		// set if the device is sweeping
#define SWP_UP				0x00000008		// set if the device is ramping up
#define SWP_REPEAT			0x00000010		// set if the device is in continuous ramp mode
#define SWP_BIDIRECTIONAL	0x00000020		// set if the device is in bi-directional ramp mode
#define PROFILE_ACTIVE		0x00000040		// set if a profile is playing


VNX_ATTEN_API void VB6_API fnLDA_SetTestMode(bool testmode);
VNX_ATTEN_API int VB6_API fnLDA_GetNumDevices();
VNX_ATTEN_API int VB6_API fnLDA_GetDevInfo(DEVID *ActiveDevices);
VNX_ATTEN_API int VB6_API fnLDA_GetModelName(DEVID deviceID, char *ModelName);
VNX_ATTEN_API int VB6_API fnLDA_InitDevice(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_CloseDevice(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetSerialNumber(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetDLLVersion();
VNX_ATTEN_API int VB6_API fnLDA_GetDeviceStatus(DEVID deviceID);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetAttenuation(DEVID deviceID, int attenuation);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetRampStart(DEVID deviceID, int rampstart);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetRampEnd(DEVID deviceID, int rampstop);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetAttenuationStep(DEVID deviceID, int attenuationstep);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetAttenuationStepTwo(DEVID deviceID, int attenuationstep2);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetDwellTime(DEVID deviceID, int dwelltime);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetDwellTimeTwo(DEVID deviceID, int dwelltime2);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetIdleTime(DEVID deviceID, int idletime);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetHoldTime(DEVID deviceID, int holdtime);

VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetProfileElement(DEVID deviceID, int index, int attenuation);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetProfileCount(DEVID deviceID, int profilecount);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetProfileIdleTime(DEVID deviceID, int idletime);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetProfileDwellTime(DEVID deviceID, int dwelltime);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_StartProfile(DEVID deviceID, int mode);

VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetRFOn(DEVID deviceID, bool on);

VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetRampDirection(DEVID deviceID, bool up);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetRampMode(DEVID deviceID, bool mode);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SetRampBidirectional(DEVID deviceID, bool bidir_enable);
VNX_ATTEN_API LVSTATUS VB6_API fnLDA_StartRamp(DEVID deviceID, bool go);

VNX_ATTEN_API LVSTATUS VB6_API fnLDA_SaveSettings(DEVID deviceID);

VNX_ATTEN_API int VB6_API fnLDA_GetAttenuation(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetRampStart(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetRampEnd(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetDwellTime(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetDwellTimeTwo(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetIdleTime(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetHoldTime(DEVID deviceID);

VNX_ATTEN_API int VB6_API fnLDA_GetAttenuationStep(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetAttenuationStepTwo(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetRF_On(DEVID deviceID);

VNX_ATTEN_API int VB6_API fnLDA_GetProfileElement(DEVID deviceID, int index);
VNX_ATTEN_API int VB6_API fnLDA_GetProfileCount(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetProfileDwellTime(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetProfileIdleTime(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetProfileIndex(DEVID deviceID);

VNX_ATTEN_API int VB6_API fnLDA_GetMaxAttenuation(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetMinAttenuation(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetMinAttenStep(DEVID deviceID);
VNX_ATTEN_API int VB6_API fnLDA_GetFeatures(DEVID deviceID);

#ifdef __cplusplus
  #if (VNX_ANSI || VNX_STDCALL)
	}
  #endif
#endif