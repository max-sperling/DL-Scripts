function Invoke-Synchronized {
    param (
        [Parameter(Mandatory)] [System.Object] $SyncObject,
        [Parameter(Mandatory)] [ScriptBlock] $ScriptBlock
    )

    [System.Threading.Monitor]::Enter($SyncObject)
    try {
        Invoke-Command -ScriptBlock $ScriptBlock
    } finally {
        [System.Threading.Monitor]::Exit($SyncObject)
    }
}

function Print-Message {
    param (
        [Parameter(Mandatory)] [string] $Message
    )

    Write-Host "$(Get-Date) $Message"
}

function Remove-Arguments {
    param (
        [Parameter(Mandatory)] [string] $Text
    )

    return $Text.split("?")[0]
}
