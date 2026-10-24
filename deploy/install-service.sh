#!/usr/bin/env bash
# 把 yichengs.tw 網站安裝成 systemd 服務，開機自動啟動。
#
# 用法：
#   sudo deploy/install-service.sh              安裝並啟動（127.0.0.1:8000）
#   sudo deploy/install-service.sh --port 8080  改用其他 port
#   deploy/install-service.sh --dry-run         只印出服務設定，不做任何變更
#
# 安裝後：
#   sudo systemctl restart yichengs-web   更新程式碼後重新啟動
#   systemctl status yichengs-web         查看狀態
#   journalctl -u yichengs-web -f         查看即時紀錄
set -euo pipefail

SERVICE=yichengs-web
PORT=8000
DRY_RUN=0
ORIG_ARGS="$*"

while [ $# -gt 0 ]; do
	case "$1" in
		--port) PORT="${2:-}"; shift 2 || { echo "--port 後面要接數字" >&2; exit 1; } ;;
		--dry-run) DRY_RUN=1; shift ;;
		-h|--help) sed -n '2,12p' "$0"; exit 0 ;;
		*) echo "不認得的參數：$1（用 --help 看用法）" >&2; exit 1 ;;
	esac
done
case "$PORT" in ''|*[!0-9]*) echo "port 必須是數字：$PORT" >&2; exit 1 ;; esac

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="${SUDO_USER:-$(id -un)}"
if ! RUN_GROUP="$(id -gn "$RUN_USER" 2>/dev/null)"; then
	RUN_GROUP="$(id -g "$RUN_USER")"   # 群組沒有名稱時改用 GID
fi
VENV="$PROJECT_DIR/venv"
UNIT_FILE="/etc/systemd/system/$SERVICE.service"
ENV_FILE="/etc/$SERVICE.env"

[ -f "$PROJECT_DIR/manage.py" ] || { echo "找不到 $PROJECT_DIR/manage.py" >&2; exit 1; }
case "$PROJECT_DIR" in
	*[[:space:]]*|*'|'*|*'&'*) echo "專案路徑不能有空白或 | & 符號：$PROJECT_DIR" >&2; exit 1 ;;
esac

unit="$(sed -e "s|@PROJECT_DIR@|$PROJECT_DIR|g" \
            -e "s|@USER@|$RUN_USER|g" \
            -e "s|@GROUP@|$RUN_GROUP|g" \
            -e "s|@PORT@|$PORT|g" \
            "$PROJECT_DIR/deploy/$SERVICE.service")"

if [ "$DRY_RUN" -eq 1 ]; then
	echo "# 會寫入 $UNIT_FILE（使用者 $RUN_USER）："
	printf '%s\n' "$unit"
	exit 0
fi

[ "$(id -u)" -eq 0 ] || { echo "請用 sudo 執行：sudo $0 $ORIG_ARGS" >&2; exit 1; }
command -v systemctl >/dev/null || { echo "這台機器沒有 systemd" >&2; exit 1; }

as_user() { sudo -u "$RUN_USER" -H "$@"; }

# 1. Python 虛擬環境與套件
if [ ! -x "$VENV/bin/python" ]; then
	echo "==> 建立虛擬環境 $VENV"
	as_user python3 -m venv "$VENV"
fi
if ! as_user "$VENV/bin/python" -c 'import django' 2>/dev/null; then
	echo "==> 安裝套件（requirements.txt）"
	as_user "$VENV/bin/pip" install --quiet --upgrade pip
	as_user "$VENV/bin/pip" install --quiet -r "$PROJECT_DIR/requirements.txt"
fi

# 2. Django 金鑰：只在第一次安裝時產生，之後沿用
if [ ! -f "$ENV_FILE" ]; then
	echo "==> 產生 $ENV_FILE"
	( umask 077; printf 'DJANGO_SECRET_KEY=%s\n' "$("$VENV/bin/python" -c 'import secrets; print(secrets.token_urlsafe(50))')" > "$ENV_FILE" )
fi

# 3. 確認網站設定沒問題，並建立／更新資料庫（db.sqlite3 不在 repo 裡）
as_user "$VENV/bin/python" "$PROJECT_DIR/manage.py" check
as_user "$VENV/bin/python" "$PROJECT_DIR/manage.py" migrate --noinput

# 4. port 被其他程式佔用（例如手動跑的 runserver）就先停下來
if ! systemctl is-active --quiet "$SERVICE" && command -v ss >/dev/null && ss -Hltn "sport = :$PORT" | grep -q .; then
	echo "port $PORT 已經被其他程式使用，請先關掉它再重新執行：" >&2
	ss -ltnp "sport = :$PORT" >&2
	exit 1
fi

# 5. 安裝服務、設定開機啟動並立即啟動
echo "==> 安裝 $UNIT_FILE"
printf '%s\n' "$unit" > "$UNIT_FILE"
systemctl daemon-reload
systemctl enable --quiet "$SERVICE"
systemctl restart "$SERVICE"

sleep 2
if systemctl is-active --quiet "$SERVICE"; then
	echo "==> 完成：$SERVICE 已啟動，並設為開機自動啟動（http://127.0.0.1:$PORT/）"
else
	echo "==> $SERVICE 沒有成功啟動，最近的紀錄：" >&2
	journalctl -u "$SERVICE" -n 20 --no-pager >&2
	exit 1
fi
