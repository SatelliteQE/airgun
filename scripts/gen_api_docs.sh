#!/usr/bin/env bash
set -euo pipefail

find "airgun/" -maxdepth 1 -type f -not -path "*__*" -o -type d -not -path "*__*" -not -path "*/" | sort | while read -r file; do
    if [ -f "$file" ]; then
        file="${file%.*}"
    fi
    file_dots="${file//\//.}"
    cat >"docs/api/${file_dots}.rst" <<EOF
:mod:\`${file_dots}\`
$(printf %$(( 7 + ${#file_dots} ))s | tr ' ' =)

.. automodule:: ${file_dots}
    :members:
EOF
    if [ -d "$file" ]; then
        find "${file}" -type f -not -path "*__*" | sort | while read -r file_name; do
            module_name="${file_name%.py}"
            module_name="${module_name//\//.}"

            cat >>"docs/api/${file_dots}.rst" <<EOF

:mod:\`${module_name}\`
$(printf %$(( 7 + ${#module_name} ))s | tr ' ' -)

.. automodule:: ${module_name}
   :members:
EOF
        done
    fi
done
