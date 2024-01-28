Import-Module "$PSScriptRoot\Common.psm1"

function Download-Playlist {
    param (
        [Parameter(Mandatory)] [string] $PlaylistLink,
        [Parameter(Mandatory)] [string] $OutputFile
    )

    $StorageLink = $PlaylistLink.Substring(0, $PlaylistLink.LastIndexOf("/"))
    $PlaylistFile = $PlaylistLink.Substring($PlaylistLink.LastIndexOf("/")+1)

    $NoError = Download-PlaylistFile $StorageLink $PlaylistFile
    if ($NoError) { Print-Message "Playlist file downloaded" }
    else { return $false }

    $NoError = Download-MediaFiles $PlaylistFile $StorageLink
    if ($NoError) { Print-Message "Media files downloaded" }
    else { return $false }

    $NoError = Concat-MediaFiles $PlaylistFile $OutputFile
    if ($NoError) { Print-Message "Media files concatenated" }
    else { return $false }

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
        Print-Message "$StorageLink/$PlaylistFile $_.Exception.Message"
        return $false
    }

    return $true
}

function Download-MediaFiles {
    param (
        [Parameter(Mandatory)] [string] $PlaylistFile,
        [Parameter(Mandatory)] [string] $StorageLink
    )

    $ProgressPreference = "SilentlyContinue"

    $NoError = $true

    $ThreadArgs = @{
        PrintMsgStr = ${function::Print-Message}.ToString()
        InvSyncStr = ${function::Invoke-Synchronized}.ToString()
        SyncObject = [System.Object]::new()
    }

    Get-Content $PlaylistFile | Where-Object {$_ -NotMatch "^#"} | ForEach-Object -Parallel {

        $MediaFile = $_.Substring($_.LastIndexOf("/")+1)

        try {
            Invoke-WebRequest "$using:StorageLink/$MediaFile" -OutFile $MediaFile
        } catch {
            ${function:Print-Message} = $using:ThreadArgs.PrintMsgStr
            ${function:Invoke-Synchronized} = $using:ThreadArgs.InvSyncStr

            Invoke-Synchronized $using:ThreadArgs.SyncObject {
                Print-Message "$using:StorageLink/$MediaFile $_.Exception.Message"
                $NoError = $using:NoError
                $NoError = $false
            }
        }

    } -ThrottleLimit 10

    return $NoError
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
