Fly-in test maps pack (30 files)

Files 01-24 are mainly for parser/validation error handling.
Files 25-30 are valid maps to test normal output, restricted zones, priority tie-breaks,
node capacity, edge capacity, and comments/blank lines.

Suggested batch test command:
for f in fly_in_error_maps_30/*.txt; do
    echo "========================================"
    echo "Testing: $f"
    python3 -m src "$f" || true
    echo
done
