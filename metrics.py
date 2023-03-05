import os, shutil, socket, subprocess, boto3
from datetime import datetime

def get_upgradable_packages():
    """
    Returns the number of upgradable packages if it is supported. Currently
    only Debian apt and RedHat dnf are supported.
    """
    # Debian
    if shutil.which("apt") is not None:
        cmd = [ "apt", "-qq", "list", "--upgradable" ]
    
    # RedHat
    elif shutil.which("dnf") is not None:
        cmd = [ "dnf", "-q", "check-update" ]
    
    else:
        return -1 # Not supported
    
    out, _ = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ).communicate()
    
    return len( # Count the lines (wc -l)
        list( # Convert to list
          filter( # Filter out empty lines (grep -v ^$)
            lambda x: len(x) > 0, out.decode('utf-8').splitlines()
          )
        )
    )

def get_days_since_last_reboot():
    """
    Returns the number of days since the last reboot using `uptime`.
    """
    out, _ = subprocess.Popen( [ "uptime", "-s" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT ).communicate()
    boot_time = datetime.strptime( out.decode('utf-8').replace("\n", ""), "%Y-%m-%d %H:%M:%S" )
    return ( datetime.now() - boot_time ).days

def get_os_major_version():
    """
    Returns major part of the OS version. Useful when keeping track of OSes that
    are not supported anymore like Ubuntu 16.04. It tried first with lsb_release
    then with file /etc/lsb-release and finally with file /etc/os-release.
    """
    version = "-1"
    
    # Using lsb_release binary if present
    if shutil.which( "lsb_release" ) is not None:
        out, _ = subprocess.Popen( [ "lsb_release", "-rs" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT ).communicate()
        version = out.decode('utf-8')
    
    # Using /etc/lsb-release file if present
    elif os.path.isfile( "/etc/lsb-release" ):
        with open( "/etc/lsb-release", "r" ) as f:
            for line in f:
                if line.startswith( "DISTRIB_RELEASE=" ):
                    version = line.split("=")[1]
                    break
    
    # Using /etc/os-release file if present
    elif os.path.isfile( "/etc/os-release" ):
        with open( "/etc/os-release", "r" ) as f:
            for line in f:
                if line.startswith( "VERSION_ID=" ):
                    version = line.split("=")[1]
                    break
    
    return int( version.strip('"').split(".")[0] )

def create_metric(name, value, unit, dimensions):
    """
    Creates a CloudWatch MetricData object.
    """
    return {
        "MetricName": name,
        "Dimensions": dimensions,
        "Unit": unit,
        "Value": value
    }

if __name__ == "__main__":
    # Define dimensions for CloudWatch. We will use hostname and distribution
    # if it is defined in the environment variables. In cron, this is defined
    # as OS_DISTRIBUTION="Ubuntu" before the executable.
    dimensions = [
        { "Name": "Hostname", "Value": socket.gethostname() },
        { "Name": "Distribution", "Value": os.environ["OS_DISTRIBUTION"] if "OS_DISTRIBUTION" in os.environ else "Unknown" }
    ]

    # Create MetricData objects for each function.
    packages = create_metric( "UpgradablePackages", get_upgradable_packages(), "Count", dimensions)
    days_since_last_reboot = create_metric( "DaysSinceLastReboot", get_days_since_last_reboot(), "Count", dimensions)
    os_major_version = create_metric( "OSMajorVersion", get_os_major_version(), "None", dimensions)

    # TODO: Change this to your own region.
    cw = boto3.client( "cloudwatch", region_name="eu-central-1" )
    cw.put_metric_data(
        Namespace = "SystemState",
        MetricData = [
            packages,
            days_since_last_reboot,
            os_major_version
        ]
    )