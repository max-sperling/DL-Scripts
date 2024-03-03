using namespace System.Collections

Import-Module "$PSScriptRoot\Common-Functions.psm1"

function Download-Playlist {
    param (
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $PlaylistLink,
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $OutputFile
    )

    $NoError = $true
    $StorageLink = $PlaylistLink.Substring(0, $PlaylistLink.LastIndexOf("/"))
    $PlaylistFile = $PlaylistLink.Substring($PlaylistLink.LastIndexOf("/")+1)
    $PlaylistFileWA = Remove-Arguments $PlaylistFile

    $NoError = Download-PlaylistFile $StorageLink $PlaylistFile $PlaylistFileWA
    if ($NoError) {
        Print-Message "Playlist file download successful"
    } else {
        Print-Message "Playlist file download failed"
        return $false
    }

    $FailedFiles = New-Object ArrayList
    $NoError = Download-MediaFiles $PlaylistFileWA $StorageLink $FailedFiles
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

    $NoError = Concat-MediaFiles $PlaylistFileWA $OutputFile
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
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $StorageLink,
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $PlaylistFile,
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $PlaylistFileWA
    )

    $ProgressPreference = "SilentlyContinue"

    try {
        Invoke-WebRequest "$StorageLink/$PlaylistFile" -OutFile $PlaylistFileWA
    } catch {
        Print-Message "File: $StorageLink/$PlaylistFileWA, Error: $($_.Exception.Message)"
        return $false
    }

    return $true
}

function Download-MediaFiles {
    param (
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $PlaylistFileWA,
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $StorageLink,
        [Parameter(Mandatory)] [ArrayList] [ValidateNotNull()] [AllowEmptyCollection()] $FailedFiles
    )

    $ProgressPreference = "SilentlyContinue"

    $ThreadArgs = New-Object Hashtable(@{ 
        NoError = $true
        PrintMsgStr = ${function::Print-Message}.ToString()
        RemArgsStr = ${function::Remove-Arguments}.ToString()
        InvSyncStr = ${function::Invoke-Synchronized}.ToString()
        SyncObject = [System.Object]::new()
    })

    Get-Content $PlaylistFileWA | Where-Object {$_ -NotMatch "^#"} | ForEach-Object -Parallel {

        $MediaFile = $_.Substring($_.LastIndexOf("/")+1)

        ${function:Remove-Arguments} = $using:ThreadArgs.RemArgsStr
        $MediaFileWA = Remove-Arguments $MediaFile

        try {
            Invoke-WebRequest "$using:StorageLink/$MediaFile" -OutFile $MediaFileWA
        } catch {
            ${function:Invoke-Synchronized} = $using:ThreadArgs.InvSyncStr

            Invoke-Synchronized $using:ThreadArgs.SyncObject {
                ($using:ThreadArgs).NoError = $false

                ${function:Print-Message} = $using:ThreadArgs.PrintMsgStr
                Print-Message "File: $using:StorageLink/$MediaFileWA, Error: $($_.Exception.Message)"

                ($using:FailedFiles).Add($MediaFile) > $null
            }
        }

    } -ThrottleLimit 10

    return $ThreadArgs.NoError
}

function Download-Files {
    param (
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $StorageLink,
        [Parameter(Mandatory)] [ArrayList] [ValidateNotNullOrEmpty()] $FileList
    )

    $ProgressPreference = "SilentlyContinue"

    $ThreadArgs = New-Object Hashtable(@{ 
        NoError = $true
        PrintMsgStr = ${function::Print-Message}.ToString()
        RemArgsStr = ${function::Remove-Arguments}.ToString()
        InvSyncStr = ${function::Invoke-Synchronized}.ToString()
        SyncObject = [System.Object]::new()
    })

    $FileList | ForEach-Object -Parallel {

        $MediaFile = $_

        ${function:Remove-Arguments} = $using:ThreadArgs.RemArgsStr
        $MediaFileWA = Remove-Arguments $MediaFile

        try {
            Invoke-WebRequest "$using:StorageLink/$MediaFile" -OutFile $MediaFileWA
        } catch {
            ${function:Invoke-Synchronized} = $using:ThreadArgs.InvSyncStr

            Invoke-Synchronized $using:ThreadArgs.SyncObject {
                ($using:ThreadArgs).NoError = $false

                ${function:Print-Message} = $using:ThreadArgs.PrintMsgStr
                Print-Message "File: $using:StorageLink/$MediaFileWA, Error: $($_.Exception.Message)"
            }
        }

    } -ThrottleLimit 10

    return $ThreadArgs.NoError
}

function Concat-MediaFiles {
    param (
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $PlaylistFileWA,
        [Parameter(Mandatory)] [string] [ValidateNotNullOrEmpty()] $OutputFile
    )

    $Concat = "concat:"

    Get-Content $PlaylistFileWA | Where-Object {$_ -NotMatch "^#"} | ForEach-Object {
        $MediaFile = $_.Substring($_.LastIndexOf("/")+1)
        $MediaFileWA = Remove-Arguments $MediaFile

        $Concat += "$MediaFileWA|"
    }

    ffmpeg -i $Concat -c copy $OutputFile

    return $true
}

Export-ModuleMember -Function Download-Playlist
