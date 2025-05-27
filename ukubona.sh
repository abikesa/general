# deploy.sh
#!/bin/bash
cd "$(dirname "$0")"
python kitabo/ensi/python/ukubona.py kitabo/ensi/wiki --branch double-commit` --message "🎓 Ritual commit after the mess"
