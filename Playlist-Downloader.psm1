using namespace System.Collections

Import-Module "$PSScriptRoot\Common-Functions.psm1"

function Download-Playlist {
    param (
        [Parameter(Mandatory)] [string] $PlaylistLink,
        [Parameter(Mandatory)] [string] $OutputFile
    )

    $Successful = $true

    $StorageLink = $PlaylistLink.Substring(0, $PlaylistLink.LastIndexOf("/"))
    $PlaylistFileWA = $PlaylistLink.Substring($PlaylistLink.LastIndexOf("/")+1)
    $PlaylistFile = Remove-Arguments $PlaylistFileWA

    # Download playlist file
    $Successful = Download-PlaylistFile -MaxIterations 3 -StorageLink $StorageLink -PlaylistFileWA $PlaylistFileWA
    if (!$Successful) { return $false }

    # Download media files
    $Successful = Download-MediaFiles -MaxIterations 3 -StorageLink $StorageLink -PlaylistFile $PlaylistFile
    if (!$Successful) { return $false }

    # Concat media files
    $Successful = Concat-MediaFiles -PlaylistFile $PlaylistFile -OutputFile $OutputFile
    if (!$Successful) { return $false }

    return $true
}

function Download-PlaylistFile {
    param (
        [Parameter(Mandatory)] [uint32] $MaxIterations,
        [Parameter(Mandatory)] [string] $StorageLink,
        [Parameter(Mandatory)] [string] $PlaylistFileWA
    )

    $Successful = $false

    $FileList = [ArrayList]@(
        $PlaylistFileWA)

    $FuncArgs = [Hashtable]@{
        StorageLink = $StorageLink
        FileList = $FileList}

    $Successful = Invoke-UntilSuccessful `
        -MaxIterations $MaxIterations `
        -ScriptBlock ${function:Download-Files} `
        -Arguments $FuncArgs

    if ($Successful) {
        Print-Message "Playlist file download successful"
    } else {
        Print-Message "Playlist file download failed"
    }

    return $Successful
}

function Download-MediaFiles {
    param (
        [Parameter(Mandatory)] [uint32] $MaxIterations,
        [Parameter(Mandatory)] [string] $StorageLink,
        [Parameter(Mandatory)] [string] $PlaylistFile
    )

    $Successful = $false

    $FileList = New-Object ArrayList
    Get-Content $PlaylistFile | Where-Object {$_ -NotMatch "^#"} | ForEach-Object {
        $FileList.Add($_)
    }

    $FuncArgs = [Hashtable]@{
        StorageLink = $StorageLink
        FileList = $FileList}

    $Successful = Invoke-UntilSuccessful `
        -MaxIterations $MaxIterations `
        -ScriptBlock ${function:Download-Files} `
        -Arguments $FuncArgs

    if ($Successful) {
        Print-Message "Media files download successful"
    } else {
        Print-Message "Media files download failed"
    }

    return $Successful
}

function Download-Files {
    param (
        [Parameter(Mandatory)] [string] $StorageLink,
        [Parameter(Mandatory)] [ArrayList] $FileList
    )

    $ProgressPreference = "SilentlyContinue"

    $ThreadArgs = New-Object Hashtable(@{
        SyncObject = [System.Object]::new()

        Successful = $true
        FailedFiles = [ArrayList]::new()

        PrintMsgStr = ${function::Print-Message}.ToString()
        RemArgsStr = ${function::Remove-Arguments}.ToString()
        InvSyncStr = ${function::Invoke-Synchronized}.ToString()
    })

    $FileList | ForEach-Object -Parallel {

        $FileWA = $_

        ${function:Remove-Arguments} = $using:ThreadArgs.RemArgsStr
        $File = Remove-Arguments $FileWA

        try {
            Invoke-WebRequest "$using:StorageLink/$FileWA" -OutFile $File
        } catch {
            ${function:Invoke-Synchronized} = $using:ThreadArgs.InvSyncStr

            Invoke-Synchronized $using:ThreadArgs.SyncObject {
                ($using:ThreadArgs).Successful = $false

                ${function:Print-Message} = $using:ThreadArgs.PrintMsgStr
                Print-Message "File: $using:StorageLink/$File, Error: $($_.Exception.Message)"

                ($using:ThreadArgs).FailedFiles.Add($FileWA) > $null
            }
        }

    } -ThrottleLimit 10

    $FileList = $ThreadArgs.FailedFiles

    return $ThreadArgs.Successful
}

function Concat-MediaFiles {
    param (
        [Parameter(Mandatory)] [string] $PlaylistFile,
        [Parameter(Mandatory)] [string] $OutputFile
    )

    $Concat = "concat:"

    Get-Content $PlaylistFile | Where-Object {$_ -NotMatch "^#"} | ForEach-Object {
        $MediaFileWA = $_.Substring($_.LastIndexOf("/")+1)
        $MediaFile = Remove-Arguments $MediaFileWA

        $Concat += "$MediaFile|"
    }

    ffmpeg -i $Concat -c copy $OutputFile

    Print-Message "Media files concat successful"

    return $true
}

Export-ModuleMember -Function Download-Playlist
