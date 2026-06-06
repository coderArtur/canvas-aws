from config import EMAIL, SENHA, URL_LOGIN

def realizar_login(page):
    page.goto(URL_LOGIN)
    page.locator('#pseudonym_session_unique_id').fill(EMAIL)
    page.locator('input[type="password"]').first.fill(SENHA)
    page.locator('input[type="submit"]').first.click()
    page.wait_for_load_state('networkidle')
