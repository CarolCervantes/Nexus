param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)
$scriptPath = Join-Path $PSScriptRoot "nexus_core.py"
python $scriptPath @ArgsList
