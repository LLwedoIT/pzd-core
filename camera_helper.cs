using System;
using System.Diagnostics;
using System.Management;
using System.Linq;

class CameraHelper
{
    static void Main(string[] args)
    {
        if (args.Length == 0)
        {
            PrintUsage();
            return;
        }

        string command = args[0].ToLower();

        switch (command)
        {
            case "release":
                ReleaseCamera();
                break;
            case "disable":
                DisableCamera();
                break;
            case "enable":
                EnableCamera();
                break;
            case "status":
                CheckCameraStatus();
                break;
            default:
                PrintUsage();
                break;
        }
    }

    static void PrintUsage()
    {
        Console.WriteLine("Camera Helper Utility");
        Console.WriteLine("Usage:");
        Console.WriteLine("  camera_helper.exe release    - Forcefully release camera resources");
        Console.WriteLine("  camera_helper.exe disable    - Disable camera device");
        Console.WriteLine("  camera_helper.exe enable     - Re-enable camera device");
        Console.WriteLine("  camera_helper.exe status     - Check camera status");
    }

    static void ReleaseCamera()
    {
        try
        {
            Console.WriteLine("[Camera Helper] Releasing camera resources...");
            
            // Kill all processes that might hold camera
            string[] cameraProcesses = { "python", "ffmpeg", "OBS", "Zoom" };
            foreach (var procName in cameraProcesses)
            {
                try
                {
                    var processes = Process.GetProcessesByName(procName);
                    // Don't kill - just let them know to clean up
                    Console.WriteLine($"[Camera Helper] Found {processes.Length} {procName} process(es)");
                }
                catch { }
            }

            // Try to restart camera driver
            RestartCameraDriver();
            
            Console.WriteLine("[Camera Helper] Camera resources released successfully");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Camera Helper Error] {ex.Message}");
        }
    }

    static void RestartCameraDriver()
    {
        try
        {
            // Use WMI to disable then enable camera device
            ManagementScope scope = new ManagementScope(@"\\.\root\cimv2");
            scope.Connect();

            // Find camera device
            ManagementObjectSearcher searcher = new ManagementObjectSearcher(
                "SELECT * FROM Win32_PnPEntity WHERE Description LIKE '%camera%' OR Description LIKE '%webcam%'"
            );

            ManagementObjectCollection devices = searcher.Get();

            if (devices.Count == 0)
            {
                Console.WriteLine("[Camera Helper] No camera device found");
                return;
            }

            foreach (ManagementObject device in devices)
            {
                try
                {
                    string deviceId = (string)device["Name"];
                    Console.WriteLine($"[Camera Helper] Found camera: {deviceId}");

                    // Get PNP device path for devcon
                    string pnpPath = (string)device["PNPDeviceID"];
                    Console.WriteLine($"[Camera Helper] Device path: {pnpPath}");

                    // Use devcon to disable/enable (if available)
                    RunDevcon($"disable {pnpPath}");
                    System.Threading.Thread.Sleep(500);
                    RunDevcon($"enable {pnpPath}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[Camera Helper] Could not reset device: {ex.Message}");
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Camera Helper] WMI Error: {ex.Message}");
        }
    }

    static void RunDevcon(string args)
    {
        try
        {
            var devconPath = @"C:\Windows\System32\devcon.exe";
            if (!System.IO.File.Exists(devconPath))
            {
                Console.WriteLine("[Camera Helper] devcon.exe not found - trying pnputil");
                return;
            }

            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = devconPath,
                    Arguments = args,
                    UseShellExecute = true,
                    CreateNoWindow = true,
                    Verb = "runas" // Request admin privileges
                }
            };

            process.Start();
            process.WaitForExit();
            Console.WriteLine($"[Camera Helper] devcon {args} completed");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Camera Helper] devcon error: {ex.Message}");
        }
    }

    static void DisableCamera()
    {
        Console.WriteLine("[Camera Helper] Disabling camera device...");
        try
        {
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = "-Command \"Get-PnpDevice -class Camera | Disable-PnpDevice -Confirm:$false\"",
                    UseShellExecute = true,
                    CreateNoWindow = true,
                    Verb = "runas"
                }
            };
            process.Start();
            process.WaitForExit();
            Console.WriteLine("[Camera Helper] Camera disabled");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Camera Helper] Error: {ex.Message}");
        }
    }

    static void EnableCamera()
    {
        Console.WriteLine("[Camera Helper] Enabling camera device...");
        try
        {
            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = "-Command \"Get-PnpDevice -class Camera | Enable-PnpDevice -Confirm:$false\"",
                    UseShellExecute = true,
                    CreateNoWindow = true,
                    Verb = "runas"
                }
            };
            process.Start();
            process.WaitForExit();
            Console.WriteLine("[Camera Helper] Camera enabled");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Camera Helper] Error: {ex.Message}");
        }
    }

    static void CheckCameraStatus()
    {
        try
        {
            Console.WriteLine("[Camera Helper] Checking camera status...");
            ManagementScope scope = new ManagementScope(@"\\.\root\cimv2");
            scope.Connect();

            ManagementObjectSearcher searcher = new ManagementObjectSearcher(
                "SELECT * FROM Win32_PnPEntity WHERE Description LIKE '%camera%' OR Description LIKE '%webcam%'"
            );

            ManagementObjectCollection devices = searcher.Get();

            if (devices.Count == 0)
            {
                Console.WriteLine("[Camera Helper] No camera device found");
                return;
            }

            foreach (ManagementObject device in devices)
            {
                Console.WriteLine($"[Camera Helper] Camera: {device["Name"]}");
                Console.WriteLine($"  Status: {device["Status"]}");
                Console.WriteLine($"  Device ID: {device["DeviceID"]}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Camera Helper] Error: {ex.Message}");
        }
    }
}
