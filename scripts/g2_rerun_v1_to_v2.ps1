# ═══════════════════════════════════════════════════════════════════
# TALLENTIN — G2 batch re-run | S149 | 2026-07-03
# Re-runs 26 v1-contract submissions through recruiter-report v2.
# Old v1 outputs already archived in arete.g2_v1_archive (26 rows, S149).
# Secret is typed at runtime, never stored, never printed.
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$url = "https://onzgonecbbpxwjhzqkqa.supabase.co/functions/v1/recruiter-report"

$ids = @(
  "RECR-JD-20260510T014817Z-QYB3BN",
  "RECR-JD-20260525T185152Z-PBVEF5",
  "RECR-JD-20260525T190053Z-6GDDEJ",
  "RECR-JD-20260528T225235Z-72543R",
  "RECR-JD-20260529T003256Z-QTEX9H",
  "RECR-JD-20260529T191855Z-JZXADA",
  "RECR-JD-20260601T224415Z-MB87RB",
  "RECR-JD-20260601T224654Z-EBKFBK",
  "RECR-JD-20260601T224857Z-VE75CJ",
  "RECR-JD-20260601T225107Z-22YRGR",
  "RECR-JD-20260601T225253Z-2JSDF7",
  "RECR-JD-20260601T225615Z-T2RABZ",
  "RECR-JD-20260601T231712Z-2XH698",
  "RECR-JD-20260601T231716Z-MM9YEU",
  "RECR-JD-20260601T231719Z-PJWSER",
  "RECR-JD-20260601T232930Z-C888VJ",
  "RECR-JD-20260601T232934Z-GHWB4G",
  "RECR-JD-20260601T232937Z-M6D7MT",
  "RECR-JD-20260601T233416Z-5VJXSV",
  "RECR-JD-20260601T233420Z-TKNWVA",
  "RECR-JD-20260603T222652Z-YUZFBC",
  "RECR-JD-20260603T222700Z-AZ5J2F",
  "RECR-JD-20260603T222708Z-H7MCAS",
  "RECR-JD-20260603T222716Z-2D6RR4",
  "RECR-JD-20260603T222723Z-ZHAC8D",
  "RECR-JD-20260603T222731Z-SUWM5D"
)

# ── Secret: typed hidden, held in memory only ──
$sec = Read-Host "Paste EDGE_SHARED_SECRET (input hidden)" -AsSecureString
$ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
$secret = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

$ok = 0; $fail = 0; $failedIds = @()
$total = $ids.Count
$n = 0

foreach ($id in $ids) {
  $n++
  Write-Host ("[{0}/{1}] {2} ... " -f $n, $total, $id) -NoNewline
  try {
    $resp = Invoke-RestMethod -Method Post -Uri $url `
      -Headers @{ "X-Edge-Auth" = $secret; "Content-Type" = "application/json" } `
      -Body (@{ submission_id = $id } | ConvertTo-Json) `
      -TimeoutSec 300
    if ($resp.success -eq $true) {
      Write-Host "OK (mode: $($resp.mode))" -ForegroundColor Green
      $ok++
    } else {
      Write-Host "UNEXPECTED RESPONSE" -ForegroundColor Yellow
      $fail++; $failedIds += $id
    }
  } catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    $fail++; $failedIds += $id
  }
  Start-Sleep -Seconds 5
}

$secret = $null
Write-Host ""
Write-Host "════════ G2 SUMMARY ════════"
Write-Host "OK:     $ok / $total"
Write-Host "FAILED: $fail / $total"
if ($failedIds.Count -gt 0) {
  Write-Host "Failed IDs:"
  $failedIds | ForEach-Object { Write-Host "  $_" }
}
Write-Host "Paste this summary back to SC in chat."
