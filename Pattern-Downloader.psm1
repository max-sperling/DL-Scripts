Import-Module "$PSScriptRoot\Common.psm1"

function Download-Pattern {
    param (
        [Parameter(Mandatory)] [string] $Url,
        [Parameter(Mandatory)] [string] $Pattern
    )

    $ProgressPreference = "SilentlyContinue"

    $SearchData = @{
        Text = (Invoke-WebRequest $Url).Content
        Pattern = $Pattern
    }
    Search-Items @SearchData | Select-Object -Unique | Download-Items
}

function Search-Items {
    param (
        [Parameter(Mandatory)] [string] $Text,
        [Parameter(Mandatory)] [string] $Pattern
    )

    $Text | Select-String $Pattern -AllMatches | ForEach-Object {
        $Items += @($_.Matches.Value)
    }

    return $Items
}

function Download-Items {
    param (
        [Parameter(Mandatory, ValueFromPipeline)] [string[]] $Items
    )

    begin {
        $ProgressPreference = "SilentlyContinue"
    }

    process {
        $Items | ForEach-Object {
            Print-Message "Download File: $_"
            $ItemName = $_.Substring($_.LastIndexOf("/")+1)
            Invoke-WebRequest $_ -OutFile $ItemName
        }
    }
}

Export-ModuleMember -Function Download-Pattern
