using namespace System.Collections

Import-Module "$PSScriptRoot\Common.psm1"

function Download-Playlist {
    param (
        [Parameter(Mandatory)] [string] $PlaylistLink,
        [Parameter(Mandatory)] [string] $OutputFile
    )

    $StorageLink = $PlaylistLink.Substring(0, $PlaylistLink.LastIndexOf("/"))
    $PlaylistFile = $PlaylistLink.Substring($PlaylistLink.LastIndexOf("/")+1)
    $NoError = $true

    $NoError = Download-PlaylistFile $StorageLink $PlaylistFile
    if ($NoError) {
        Print-Message "Playlist file download successful"
    } else {
        Print-Message "Playlist file download failed"
        return $false
    }

    $FailedFiles = New-Object ArrayList
    $NoError = Download-MediaFiles $PlaylistFile $StorageLink $FailedFiles
    if ($NoError) {
        Print-Message "Media files download successful"
    } else {
        Print-Message "Let's download the failed files again"

        $NoError = Download-Files $StorageLink $FailedFiles
        if ($NoError) {
            Print-Message "Media files download successful"
        } else {
            Print-Message "Media files download failed"
            return $false
        }
    }

    $NoError = Concat-MediaFiles $PlaylistFile $OutputFile
    if ($NoError) {
        Print-Message "Media files concat successful"
    } else {
        Print-Message "Media files concat failed"
        return $false
    }

    return $true
}

function Download-PlaylistFile {
    param (
        [Parameter(Mandatory)] [string] $StorageLink,
        [Parameter(Mandatory)] [string] $PlaylistFile
    )

    $ProgressPreference = "SilentlyContinue"

    try {
        Invoke-WebRequest "$StorageLink/$PlaylistFile" -OutFile $PlaylistFile
    } catch {
        Print-Message "File: $StorageLink/$MediaFile, Error: $($_.Exception.Message)"
        return $false
    }

    return $true
}

function Download-MediaFiles {
    param (
        [Parameter(Mandatory)] [string] $PlaylistFile,
        [Parameter(Mandatory)] [string] $StorageLink,
        [Parameter(Mandatory)] [ArrayList] [AllowEmptyCollection()] $FailedFiles
    )

    $ProgressPreference = "SilentlyContinue"

    $ThreadArgs = New-Object Hashtable(@{ 
        NoError = $true
        PrintMsgStr = ${function::Print-Message}.ToString()
        InvSyncStr = ${function::Invoke-Synchronized}.ToString()
        SyncObject = [System.Object]::new()
    })

    Get-Content $PlaylistFile | Where-Object {$_ -NotMatch "^#"} | ForEach-Object -Parallel {

        $MediaFile = $_.Substring($_.LastIndexOf("/")+1)

        try {
            Invoke-WebRequest "$using:StorageLink/$MediaFile" -OutFile $MediaFile
        } catch {
            ${function:Invoke-Synchronized} = $using:ThreadArgs.InvSyncStr

            Invoke-Synchronized $using:ThreadArgs.SyncObject {
                ($using:ThreadArgs).NoError = $false

                ${function:Print-Message} = $using:ThreadArgs.PrintMsgStr
                Print-Message "File: $using:StorageLink/$MediaFile, Error: $($_.Exception.Message)"

                ($using:FailedFiles).Add($MediaFile) > $null
            }
        }

    } -ThrottleLimit 10

    return $ThreadArgs.NoError
}

function Download-Files {
    param (
        [Parameter(Mandatory)] [string] $StorageLink,
        [Parameter(Mandatory)] [ArrayList] [AllowEmptyCollection()] $FileList
    )

    $ProgressPreference = "SilentlyContinue"

    $ThreadArgs = New-Object Hashtable(@{ 
        NoError = $true
        PrintMsgStr = ${function::Print-Message}.ToString()
        InvSyncStr = ${function::Invoke-Synchronized}.ToString()
        SyncObject = [System.Object]::new()
    })

    $FileList | ForEach-Object -Parallel {

        try {
            Invoke-WebRequest "$using:StorageLink/$_" -OutFile $_
        } catch {
            ${function:Invoke-Synchronized} = $using:ThreadArgs.InvSyncStr

            Invoke-Synchronized $using:ThreadArgs.SyncObject {
                ($using:ThreadArgs).NoError = $false

                ${function:Print-Message} = $using:ThreadArgs.PrintMsgStr
                Print-Message "File: $using:StorageLink/$MediaFile, Error: $($_.Exception.Message)"
            }
        }

    } -ThrottleLimit 10

    return $ThreadArgs.NoError
}

function Concat-MediaFiles {
    param (
        [Parameter(Mandatory)] [string] $PlaylistFile,
        [Parameter(Mandatory)] [string] $OutputFile
    )

    $Concat = "concat:"

    Get-Content $PlaylistFile | Where-Object {$_ -NotMatch "^#"} | ForEach-Object {
        $MediaFile = $_.Substring($_.LastIndexOf("/")+1)
        $Concat += "$MediaFile|"
    }

    ffmpeg -i $Concat -c copy $OutputFile

    return $true
}

Export-ModuleMember -Function Download-Playlist
