 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..2a5a985128a84d6b6a02638faa111c4ce1451d25
--- /dev/null
+++ b/README.md
@@ -0,0 +1,22 @@
+# Zir4h 🎱
+
+A terminal-friendly **9-ball pool game** built for **Termux**.
+
+## Run on Termux
+
+```bash
+pkg install python -y
+python3 zir4h.py
+```
+
+## How to play
+
+- Two-player local turns (`Player 1` / `Player 2`)
+- On each shot, enter:
+  - `Angle` (0-359)
+  - `Power` (1-100)
+- You must hit the **lowest-numbered ball first**.
+- Pocket the **9-ball legally** to win.
+- If you foul, turn passes.
+
+Enjoy playing **Zir4h** in your terminal.
 
EOF
)
