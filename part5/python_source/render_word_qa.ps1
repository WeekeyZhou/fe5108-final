<# Render read-only Word inputs to PDFs for local visual QA. Does not edit sources.
   Word runs hidden. PDF/PNG files belong in the ignored part5/.qa directory.
   Example: powershell -File part5/python_source/render_word_qa.ps1 -Reference
#>
param([switch]$Reference)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$qaRoot = Join-Path $repoRoot 'part5/.qa'
if ($Reference) {
    $inputs = @('part3/documents/Part3_report.docx', 'part3/documents/Part3_exhibits.docx')
} else {
    $inputs = @('part5/documents/Part5_report.docx', 'part5/documents/Part5_exhibits.docx')
}
$wordApp = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    foreach ($relativeInput in $inputs) {
        $inputFile = (Resolve-Path -LiteralPath (Join-Path $repoRoot $relativeInput)).Path
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($inputFile)
        $outDir = Join-Path $qaRoot $stem
        New-Item -Path $outDir -ItemType Directory -Force | Out-Null
        $pdfFile = Join-Path $outDir ($stem + '.pdf')
        $openedDoc = $null
        try {
            $openedDoc = $wordApp.Documents.Open($inputFile, $false, $true, $false)
            $openedDoc.Repaginate()
            $pages = $openedDoc.ComputeStatistics(2)
            $openedDoc.ExportAsFixedFormat($pdfFile, 17)
            Write-Output "$stem : $pages pages; exported $pdfFile"
        } finally {
            if ($null -ne $openedDoc) {
                $openedDoc.Close(0)
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($openedDoc) | Out-Null
            }
        }
    }
} finally {
    if ($null -ne $wordApp) {
        $wordApp.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) | Out-Null
    }
}
