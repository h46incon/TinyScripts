
using System; 
using System.Runtime.InteropServices; 

namespace @INCON_SCRIPTING_NAMESPACE@ 
{
    [StructLayout(LayoutKind.Sequential)] 
    struct DEVMODE 
    { 
       [MarshalAs(UnmanagedType.ByValTStr,SizeConst=32)]
       public string dmDeviceName;

       public short  dmSpecVersion;
       public short  dmDriverVersion;
       public short  dmSize;
       public short  dmDriverExtra;
       public int    dmFields;
       public int    dmPositionX;
       public int    dmPositionY;
       public int    dmDisplayOrientation;
       public int    dmDisplayFixedOutput;
       public short  dmColor;
       public short  dmDuplex;
       public short  dmYResolution;
       public short  dmTTOption;
       public short  dmCollate;

       [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
       public string dmFormName;

       public short  dmLogPixels;
       public short  dmBitsPerPel;
       public int    dmPelsWidth;
       public int    dmPelsHeight;
       public int    dmDisplayFlags;
       public int    dmDisplayFrequency;
       public int    dmICMMethod;
       public int    dmICMIntent;
       public int    dmMediaType;
       public int    dmDitherType;
       public int    dmReserved1;
       public int    dmReserved2;
       public int    dmPanningWidth;
       public int    dmPanningHeight;
    }; 

	 [Flags()]
	 public enum DisplayDeviceStateFlags : int
	 {
		///<summary>The device is part of the desktop.</summary>
		AttachedToDesktop = 0x1,
		MultiDriver = 0x2,
		///<summary>The device is part of the desktop.</summary>
		PrimaryDevice = 0x4,
		///<summary>Represents a pseudo device used to mirror application drawing for remoting or other purposes.</summary>
		MirroringDriver = 0x8,
		///<summary>The device is VGA compatible.</summary>
		VGACompatible = 0x16,
		///<summary>The device is removable; it cannot be the primary display.</summary>
		Removable = 0x20,
		///<summary>The device has more display modes than its output devices support.</summary>
		ModesPruned = 0x8000000,
		Remote = 0x4000000,
		Disconnect = 0x2000000
	 }

	 [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
	 public struct DISPLAY_DEVICE
	 {
	 [MarshalAs(UnmanagedType.U4)]
	 public int cb;
	 [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
	 public string DeviceName;
	 [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
	 public string DeviceString;
	 [MarshalAs(UnmanagedType.U4)]
	 public DisplayDeviceStateFlags StateFlags;
	 [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
	 public string DeviceID;
	 [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
	 public string DeviceKey;
	 }
	 
    class NativeMethods 
    { 
        [DllImport("user32.dll")] 
        public static extern int EnumDisplaySettings(string deviceName, int modeNum, ref DEVMODE devMode); 
        [DllImport("user32.dll")] 
        public static extern int ChangeDisplaySettings(ref DEVMODE devMode, int flags); 
        [DllImport("user32.dll")]
        public static extern bool EnumDisplayDevices(string lpDevice, uint iDevNum, ref DISPLAY_DEVICE lpDisplayDevice, uint dwFlags);

        public const int ENUM_CURRENT_SETTINGS = -1; 
        public const int CDS_UPDATEREGISTRY = 0x01; 
        public const int CDS_TEST = 0x02; 

        public const int DISP_CHANGE_SUCCESSFUL = 0; 
        public const int DISP_CHANGE_RESTART = 1; 
        public const int DISP_CHANGE_FAILED = -1;

        public const int DMDO_DEFAULT = 0;
        public const int DMDO_90 = 1;
        public const int DMDO_180 = 2;
        public const int DMDO_270 = 3;
    } 

    public class MainClass 
    { 
        static public void Main(string[] args) 
        { 
            var device = new DISPLAY_DEVICE();
            device.cb = Marshal.SizeOf(device);
			
			uint main_display_index = 0;
            NativeMethods.EnumDisplayDevices(null, main_display_index, ref device, 0);
			
			Console.WriteLine("Changing orientation: {0}  ({1})", device.DeviceName, device.DeviceString);

            DEVMODE dm = GetDevMode(); 
            if (NativeMethods.EnumDisplaySettings(device.DeviceName, NativeMethods.ENUM_CURRENT_SETTINGS, ref dm) == 0)
			{
				Console.WriteLine("Failed To Change The Resolution."); 
				return;
			}
			
			// determine new orientation based on the current orientation
			switch(dm.dmDisplayOrientation)
			{
				case NativeMethods.DMDO_DEFAULT:
					dm.dmDisplayOrientation = NativeMethods.DMDO_180;
					break;
				case NativeMethods.DMDO_180:
					dm.dmDisplayOrientation = NativeMethods.DMDO_DEFAULT;
					break;
				default:
					Console.WriteLine("will not rotate the screen cause unknown orientation");
					return;
			}

			int iRet = NativeMethods.ChangeDisplaySettings(ref dm, NativeMethods.CDS_TEST); 

			if (iRet == NativeMethods.DISP_CHANGE_FAILED) 
			{ 
				Console.WriteLine("Unable To Process Your Request. Sorry For This Inconvenience.");
				return;
			} 
			else 
			{ 
				iRet = NativeMethods.ChangeDisplaySettings(ref dm, NativeMethods.CDS_UPDATEREGISTRY); 
				switch (iRet) 
				{ 
					case NativeMethods.DISP_CHANGE_SUCCESSFUL: 
						Console.WriteLine("Success");
						return; 
					case NativeMethods.DISP_CHANGE_RESTART: 
						Console.WriteLine("You Need To Reboot For The Change To Happen");
						Console.WriteLine("If You Feel Any Problem After Rebooting Your Machine");
						Console.WriteLine("Then Try To Change Resolution In Safe Mode."); 
						return;
					default: 
						Console.WriteLine("Failed To Change The Resolution: {0}", Convert.ToString(iRet));
						return;
				} 

			} 

        } 

        private static DEVMODE GetDevMode() 
        { 
            DEVMODE dm = new DEVMODE(); 
            dm.dmDeviceName = new String(new char[32]); 
            dm.dmFormName = new String(new char[32]); 
            dm.dmSize = (short)Marshal.SizeOf(dm); 
            return dm; 
        } 
    } 
} 
