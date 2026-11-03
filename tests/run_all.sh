#!/usr/bin/env bash
# Startet alle Tests parallel und fasst das Ergebnis zusammen.
# Aufruf: bash tests/run_all.sh        (Umgebungsvariable JOBS setzt die Parallelität, Standard 4)
cd "$(dirname "$0")" || exit 1
LOG="$(mktemp -d)"
JOBS="${JOBS:-4}"
TESTS="$(ls ./*_test.py test_fc.py test_v6.py test_v9.py test_v10.py test_v11.py audit1.py audit2.py 2>/dev/null | sed 's|^\./||' | sort -u)"
echo "$TESTS" | xargs -P "$JOBS" -I{} sh -c 'timeout 600 python3 {} > "$0/{}.log" 2>&1; echo "{} exit=$?" >> "$0/done.txt"' "$LOG"
total=$(echo "$TESTS" | wc -l | tr -d ' ')
bad=0
for t in $TESTS; do
  f="$LOG/$t.log"
  if ! grep -q "^$t exit=0$" "$LOG/done.txt" || grep -Eq "^FAIL |Traceback|pageerror" "$f" || grep -Eq "^FAILS.*\[.+\]|^FAILS: [1-9]" "$f"; then
    bad=$((bad+1)); echo "FEHLER in $t"; grep -E "^FAIL |Traceback|Error|^FAILS" "$f" | head -6
  fi
done
echo "Ergebnis: $((total-bad)) von $total Tests bestanden. Logs: $LOG"
[ "$bad" -eq 0 ]
