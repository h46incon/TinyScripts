$exe_file = $args[0]
$code = Get-Content -Raw -Path $exe_file

$name_space = "ScrptingNamespace_" + (Get-Random)
$code = $code -replace "@INCON_SCRIPTING_NAMESPACE@", $name_space
# Write-Output $code

$params = $args | select

Add-Type -TypeDefinition $code -Language CSharp
Invoke-Expression ("[$name_space.MainClass]::Main" + '([Object[]]$params)')