# Mülakat Notları — Sports Betting QA Projesi

---

## BÖLÜM 1 — PROJE GENEL

**S: Bu proje ne test ediyor?**
> Bir spor bahis uygulamasının tek bahis akışını. UI (Selenium) ve API (requests) katmanında test ediyorum.

**S: Framework'ün genel yapısı nedir?**
> Python + Pytest + Selenium. Page Object Model ile UI, requests.Session ile API testleri. conftest.py'de fixture'lar tanımlı. `tests/`, `pages/`, `api/`, `config/` klasörlerine ayrılmış.

**S: Kaç tane otomasyonlu test yazdın?**
> 2 test class: `TestE2EBetPlacement` (1 E2E UI testi) ve `TestAPIStakeValidation` (9 API testi).

**S: Neden sadece 2 test class yazdın, daha fazla değil?**
> Zaman ve ROI dengesi. En kritik 2 flow'u seçtim: gelir getiren E2E akışı ve finansal bütünlük için API validasyonu. Geri kalanı manuel veya ilerleyen sprintlere bıraktım.

---

## BÖLÜM 2 — FRAMEWORK & KOD

**S: BasePage neden kullandın?**
> `driver`, `wait`, `find`, `click`, `type_text` gibi Selenium operasyonlarını tek yerde toplamak için. Her page class inheritance ile bunları miras alıyor. DRY prensibi — UI operasyonu eklemek istersen sadece `BasePage`'i güncelliyorsun.

**S: `@staticmethod` ne zaman kullanılır?**
> Metod `self` veya `cls` kullanmıyorsa. Saf utility fonksiyon. Instance state'e ihtiyaç yok demektir.

**S: `requests.Session()` neden kullandın?**
> Header'ları (`x-user-id`, `Content-Type`) bir kez set edip tüm requestlerde persist etmek için. TCP bağlantısını yeniden kullandığı için daha performanslı. Her request'te tekrar yazmak gerekmez.

**S: `place_bet_raw` neden ayrı bir metod?**
> Negatif testlerde API'ye geçersiz/eksik payload göndermek gerekiyor. `place_bet` her zaman 3 parametre zorunlu kılıyor — raw metod arbitrary dict göndermeme izin veriyor.

**S: `is_visible()` neden exception fırlatmıyor, bool dönüyor?**
> "Bu element var mı?" sorusuna cevap arıyorum. `True/False` dönünce test akışı kırılmadan `if is_visible():` ile kontrol yapılabiliyor. Exception fırlatsaydı test durur, devam edemezdi.

**S: `os.getenv` ile `os.environ[]` farkı?**
> `os.getenv("KEY", "default")` → key yoksa default döner. `os.environ["KEY"]` → key yoksa `KeyError` fırlatır. Config için `getenv` tercih edilir.

**S: `re.search` ile `re.match` farkı?**
> `re.match` sadece string başından eşleşir. `re.search` herhangi bir yerde arar. Payout text'in ortasında sayı var → `re.search` doğru.

**S: `scope="session"` ile `scope="function"` farkı?**
> `session` → test suite boyunca bir kez. `function` → her testten önce/sonra. Browser açmak pahalı → session. Balance reset izolasyon için → function (autouse=True ile otomatik).

**S: `autouse=True` ne işe yarıyor?**
> Test fonksiyonu fixture'ı parametre olarak almasa bile otomatik çalışır. Her test temiz state ile başlasın diye `reset_balance` autouse.

**S: `@pytest.mark.e2e` ve `@pytest.mark.api` ne için?**
> Test'e metadata etiketi ekler. `pytest -m api` ile sadece API testleri çalıştırılabilir. CI'da farklı stage'lerde farklı marklar çalıştırılır.

---

## BÖLÜM 3 — TEST PLANI (6 TC)

**S: Test planında kaç test case var ve öncelikleri?**
> 6 TC. Critical: TC-01 (happy path), TC-02 (stake validation), TC-06 (balance sync). High: TC-03 (yetersiz bakiye), TC-04 (odds selection update), TC-05 (payout hesaplama).

**S: TC-01 happy path'te ne doğruluyor?**
> Maç seç → stake gir → Place Bet → receipt modal (Bet ID, match, selection, stake, odds, payout, timestamp) → balance düştüğünü hem UI hem API'den kontrol et.

**S: TC-02'de spec'te bir tutarsızlık tespit ettin, ne?**
> Section 3 stake min €1.00 derken Section 4.1 €1.01 yazıyor. Section 4.1'deki değerin odds minimumu (1.01) ile karışmış olduğunu düşündüm. Testi Section 3 ve Section 4.4'e göre €1.00 olarak yazdım.

**S: TC-06 neden Critical?**
> Balance finansal değer, UI header + bet slip + API'de tutarlı olmalı. Senkronizasyon bozulursa kullanıcı yanlış bakiye görür → bozuk bahis kararı veya exploit riski.

---

## BÖLÜM 4 — BUG REPORTS (10 Bug)

**S: En kritik bug hangisi ve neden?**
> BUG-001. İki failure bir arada: UI bahis sonrası balance'ı güncellemiyor (stale kalıyor) + API'nin balance kontrolü yok. Sonuç: kullanıcı sınırsız bahis yapabiliyor, balance -€180'e düşüyor. Finansal kayıp + regülasyon ihlali.

**S: BUG-002 nedir?**
> Receipt modal payout her zaman `stake × 2` hesaplıyor, gerçek odds'u görmüyor. €5 stake, 2.45 odds → receipt €10.00 gösteriyor (doğrusu €12.25). API doğru dönüyor, bug UI render'da.

**S: BUG-001 ile BUG-002 arasında nasıl karar verdin hangisi daha kritik?**
> BUG-001 finansal zarar ve sınırsız exploit potansiyeli taşıyor. BUG-002 güven sorunudur ama ekstra para kaybettirmiyor. BUG-001 daha kritik.

**S: BUG-003 nedir?**
> Geçmiş maçlara bahis kabul ediliyor. UI "PAST" badge gösteriyor ama odds butonu aktif. API de reddemiyor. Gerçek platformda match-fixing eşdeğeri.

**S: BUG-005 neden test izolasyonunu etkiliyor?**
> `reset_balance` fixture'ı her testten önce balance'ı sıfırlamak için `POST /api/reset-balance` çağırıyor. Ama endpoint başarılı dönmesine rağmen balance sıfırlanmıyor. Testler kirli state ile başlıyor → flaky sonuçlar.

**S: BUG-004 nedir?**
> `GET /api/balance` → `currency: EUR`, `POST /api/place-bet` → `currency: USD`. API contract ihlali.

**S: Low severity bug'ları neden yazdın?**
> Kapsamlı test raporu için. Önceliği düşük ama teknik borç — ilerleyen sprintlerde düzeltilmeli. BUG-010 (125.5 vs 125.50) gibi şeyler frontend formatlamada tutarsızlığa yol açabilir.

---

## BÖLÜM 5 — STRATEJİ

**S: Neden E2E ve API testini seçtin, başka ne seçebilirdin?**
> E2E → core revenue flow, herhangi bir regression direkt iş etkisi. API → business rules UI'dan bağımsız zorlanmalı, hızlı ve deterministik. Alternatif: balance sync testi de seçilebilirdi ama BUG-001 ile zaten ortaya çıktı.

**S: Neleri manual bıraktın?**
> Filtreler (slider otomasyonu güvenilmez), error modal retry (server mock gerekir), responsive layout (görsel doğrulama), accessibility (axe/Lighthouse), concurrent betting (k6/Locust), match card styling (visual regression).

**S: CI/CD'e nasıl entegre edersin?**
> GitHub Actions workflow: `actions/setup-python` → `pip install -r requirements.txt` → `pytest tests/ -v --junitxml=results.xml`. Her PR'da otomatik çalışır.

**S: Testi scale etmek istersen ne yaparsın?**
> Kısa vade: Allure raporlama, failure screenshot. Orta vade: `@pytest.mark.parametrize` ile data-driven, `pytest-xdist` ile paralel, Pact ile contract testing. Uzun vade: k6 ile load test, Docker ile izole ortam, production synthetic monitoring.

**S: Session-scope browser ile function-scope reset kombinasyonunu neden seçtin?**
> Browser bir kez açılır (hız). Her test öncesi balance API ile sıfırlanır (izolasyon). Full browser restart yerine sadece state temizleniyor — performans + güvenilirlik dengesi.

---

## BÖLÜM 6 — GENEL PYTHON

**S: List comprehension vs loop?**
```python
# Tercih edilen
result = [x * 2 for x in items]
# Karmaşık logic varsa loop daha okunabilir
```

**S: `dict.get()` vs `dict[]`?**
> `dict["key"]` → key yoksa `KeyError`. `dict.get("key", default)` → key yoksa default döner. Güvenli erişim için `.get()`.

**S: Generator ne zaman kullanılır?**
> Büyük veri setinde bellek için. `[x for x in range(1M)]` tümünü RAM'e yükler. `(x for x in range(1M))` lazily üretir.

**S: Decorator nedir?**
> Fonksiyonu sararak davranışını değiştiren higher-order function. `@pytest.mark.api` metadata ekler, `pytest -m api` ile filtreleme sağlar.

**S: `yield` ne işe yarar? Fixture'da neden kullandın?**
> Generator yapar. Fixture'da `yield` öncesi setup, `yield` sonrası teardown. `yield driver` → driver'ı teste ver, test bitince `driver.quit()` çalıştır.

**S: `try/except` ile `finally` farkı?**
> `finally` exception olsa da olmasa da her zaman çalışır. Resource cleanup için (dosya kapatma, bağlantı kesme). Fixture'da teardown için `yield` + sonrası kod aynı işi yapar.

---

## HIZLI REFERANS — BUG ÖNEMLİLİK

| Bug | Severity | Konu |
|-----|----------|------|
| BUG-001 | Critical | UI balance güncellenmiyor + API negatif bakiye izin veriyor |
| BUG-002 | Critical | Receipt payout hep stake × 2 (hardcoded) |
| BUG-003 | High | Geçmiş maçlara bahis kabul ediliyor |
| BUG-004 | Critical | Place-bet USD dönüyor, EUR olmalı |
| BUG-005 | Critical | Reset balance persist etmiyor |
| BUG-006 | High | Receipt'te takımlar ters sırada |
| BUG-007 | High | Malformed JSON → 500 (400 olmalı) |
| BUG-008 | Low | Filtre sonrası maç sayısı etiketi güncellenmiyor |
| BUG-009 | Low | API sadece büyük harf selection kabul ediyor |
| BUG-010 | Low | Balance 125.5 dönüyor, 125.50 olmalı |

---

## HIZLI REFERANS — FIXTURE TABLOSU

| Fixture | Scope | autouse | Ne yapar |
|---------|-------|---------|---------|
| `api_client` | session | hayır | BettingClient instance'ı |
| `browser` | session | hayır | Chrome driver başlatır/kapatır |
| `reset_balance` | function | evet | Her testten önce balance sıfırlar |
| `authenticated_page` | function | hayır | BASE_URL?user-id= navigate eder |
