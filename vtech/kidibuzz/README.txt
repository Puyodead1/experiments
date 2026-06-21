boot.img - stock boot pulled from device
recovery.img - stock recovery pulled from device
magisk_patched-30700_9RD0Q.img - magisk patched boot
VCM.apk - Deobfuscated from VCM-release.ob.apk; VTech Content Manager?
VCPM.apk - Deobfuscated from VCPM-release.ob.apk; VTech Certificate Pinning Manager?
VDM.apk - Deobfuscated from VDM-release.ob.apk; VTech Download Manager?

flash with
`python mtk.py wo 0x1d80000 0x1000000 magisk_patched-30700_9RD0Q.img --parttype user --preloader preloader.bin`

# Apps

Delivered in 2 parts, a body url and a base64 encoded header. the header is retrieved from getDLContentHeaderEx/getDLContentHeaderV2. 
The header contains metadata and an encrypted content decryption key, decrypted using the device key in UniqueKey.

There are also 2 known types, one is Android APKs and the other is for non-android devices. The header for android content starts with "VITMax", while non-android starts with "VTInno".
The body for android content also starts with "InnoEnc 00.02", while non-android do not have any magic.

Seems like the part number for android content starts with 57 while non-android is 58


# random shit
http://itmax.vtechda.com/AuthPage/access_internet.txt

`/data/local/vtech/NON_VTECH_ANDROID` or `/mnt/sdcard/vtech/NON_VTECH_ANDROID` makes apps act like they're not on vtech android

`/mnt/sdcard/vtech/__vtech_enable_debug` or `/mnt/m_internal_storage/vtech/__vtech_enable_debug` to enable debug logging, requires isDeid

`/data/local/vtech/vcpmcontrol/__vtech_force_get_cert`

If `com.vtech.innotab.profile.configprovider` is a registered provider, then it is determined to be "VTech Android"

"isDeid" - a check if the EID (Equipment ID?) is a developer, true if the UniqueKey Header is not all zero.