#!/usr/bin/env python3
"""관문 페이지의 비밀번호를 정한다.

비밀번호 자체는 어디에도 저장하지 않는다. 무작위 소금(salt)을 붙여 SHA-256 으로 섞은
값만 index.html 에 넣는다. 이 스크립트를 돌리는 사람 말고는 아무도 원문을 알 수 없다.

사용: python3 tools/set_gate_password.py
      (입력한 글자는 화면에 보이지 않는다)

⚠ 이 잠금이 무엇인지 분명히 알고 쓰자.
   · 인터넷 주소(github.io)로 들어올 때만 잠긴다. 집 안 주소·로컬 파일은 그대로 열린다.
   · 관문 페이지를 가리는 장치다. 각 앱의 주소를 직접 알면 잠금을 거치지 않고 열 수 있다.
   · 섞은 값이 페이지 안에 들어 있으므로, 작정하고 대입하면 짧은 비밀번호는 뚫린다.
   즉 「아무나 우연히 들어오는 것」은 막지만 「작정한 사람」은 못 막는다.
   진짜로 막으려면 사이트 앞단에서 인증하는 방식(Cloudflare Access 등)이 필요하다.
"""
import getpass
import hashlib
import io
import os
import re
import secrets
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'index.html')


def main():
    if not os.path.exists(PAGE):
        sys.exit(f'{PAGE} 가 없습니다')
    html = io.open(PAGE, encoding='utf-8').read()
    if 'const GATE' not in html:
        sys.exit('index.html 에 로그인 장치가 없습니다. 먼저 그것부터 넣어야 합니다.')

    pw = getpass.getpass('새 비밀번호: ')
    if len(pw) < 8:
        sys.exit('8자 이상으로 정하세요 (짧으면 대입으로 뚫립니다)')
    if pw != getpass.getpass('한 번 더: '):
        sys.exit('두 번 입력한 값이 다릅니다')

    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + pw).encode('utf-8')).hexdigest()
    html = re.sub(r"const GATE = \{ *salt: *'[^']*', *hash: *'[^']*' *\}",
                  f"const GATE = {{ salt: '{salt}', hash: '{h}' }}", html, count=1)
    io.open(PAGE, 'w', encoding='utf-8').write(html)
    print('설정했습니다. index.html 을 커밋·푸시하면 인터넷 주소에서 적용됩니다.')
    print('비밀번호 원문은 저장되지 않았습니다 — 잊으면 이 스크립트를 다시 돌리세요.')


if __name__ == '__main__':
    main()
