# TDH Strategy Lab v2.0.17 — Agentic Research

v2.0.17, v2.0.16'nın mühürlü orkestrasyon ve Supervisor v2.1.8 güvenlik
çekirdeğini korur; Phoenix'e özgü tek strateji yüzeyini TDH kanıt atlasına bağlı
çok-aileli, dayanıklı araştırma döngüsüne yükseltir.

## Yeni araştırma çekirdeği

- 45 aile ve 1.534 deneylik tam atlas disk üzerinde tutulur; yalnız yerel OHLCV
  ile gerçekten yürütülebilen 8 aile ve 460 kesin tohum denetleyiciye açılır.
- LLM yalnız `novelty_frontier` içindeki değiştirilemez bir tohumu seçebilir.
  Parametre, sembol, zaman dilimi ve kontrol türü registry ile byte-stabil doğrulanır.
- Her hipotez tek bir ana değişiklik taşır. Bir strateji tohumu ancak tasarım gereği
  ayrılmazsa `atomic_bundle=true` olabilir.
- Her tohum, sonuç görülmeden önce deterministik çok-sembollü dayanıklılık paneline
  genişletilir. Adaptif sonuç kovalama yapılmaz.
- S1'de baseline ve negative control zorunludur. R/R >= 2, kazanma oranı >= %50,
  maksimum düşüş <= %10 ve pozitif beklenti tüm WFO katlarında korunmadan S2–S4'e
  geçilemez.
- `ROBUST_RESEARCH_STATE.json` 16.000 karakterle sınırlıdır;
  `EXPERIMENT_LEDGER.jsonl` append-only'dir. Yalnız controller bu kanonik durumu ve
  terfi kararını yazabilir.
- Codex hipotez üretir; karşı model S1'i geçen kısa listeyi bağımsız olarak
  yanlışlamaya çalışır. Metrikler ve terfi hiçbir zaman LLM beyanından alınmaz.
- Veri yolu yerel canonical Binance perpetual 5m Parquet'tir. Şema, sıra,
  tekrar, null, OHLCV sınırları ve dosya hash'i backtest öncesi fail-closed kontrol edilir.

Canlı/paper işlem, borsa API'si, credential, emir, deploy ve S6 eklenmemiştir.

v2.0.17, v2.0.16'nın offline, araç-izole, S1-first ve duplicate-korumalı
sözleşmesini korur. LLM'yi yalnız finansal analiz ve bağımsız değerlendirme için
kullanır; asıl deney hacmini VPS üzerinde deterministik batch backtestlerle üretir.

## Prompt bütçesi

- Codex ve Claude ilk proposer promptları worker çağrısından önce deterministik
  bounded context ile oluşturulur ve 16.000 karakter kapısına karşı 256 karakter
  güvenlik payı bırakır.
- Prompt karar-kritik frozen contract, son finansal kanıt, `novelty_frontier`, küçük
  doğrulanmış sonuç özeti ve en fazla 2 audit bulgusu taşır.
- Tam proposal/config geçmişi ve duplicate hash taraması controller-owned olarak
  diskte kalır; prompt compact edilmesi validasyonu zayıflatmaz.
- Repair promptları ayrı, daha küçük bir repair context kullanır. Untrusted
  `evaluation_plan`, config değerleri, JSON key'leri ve validation hata metni
  deterministik sınırlarla küçültülür.
- Proposal ve repair promptları en fazla 8 adapter-valid, denenmemiş config içeren
  deterministik `novelty_frontier` alır. Tam geçmiş taraması diskte kalır.

## Batch araştırma akışı

1. Tek proposer, önceki batch'in doğrulanmış finansal özetini analiz eder.
2. Controller bu kararı kayıtlı parametre, simge ve zaman dilimi ızgarası üzerinden
   en fazla 48 benzersiz adaya genişletir; sonuç görülmeden tüm sweep pre-register edilir.
3. 48 performans adayı ile baseline/negative-control deneyleri VPS'te iki worker ile
   LLM çağrısı olmadan çalışır; ilk batch en fazla 144 S1 deneyidir.
4. Yalnız S1'i geçen aday varsa VPS deterministik top-4 shortlist üretir ve karşı
   model bunu bir kez bağımsız denetler; S1'de elenen batch için reviewer tokenı harcanmaz.
5. Ham loglar prompta taşınmaz; yalnız top-8 aday, metrik/kontrol farkları ve tüm
   batch'in hata dağılımı sabit büyüklükteki context olarak sonraki analize gider.
   Top-8 context diskte korunur; gerçek prompt zarfı dolarsa controller sıralamayı
   bozmadan görünümü top-4, gerekirse top-2'ye indirir ve kaç adayın VPS'te kaldığını belirtir.
6. Adaylar önce yalnız S1'e gider; S1 geçmeden S2–S4 çalışmaz.

## Duplicate hafızası

Controller tüm geçmiş proposal config hashlerini diskte taramaya devam eder. Promptta
normalde en son 6 config'in kısa özeti yer alır; gerçek context güvenlik payını aşarsa
bu redundant görünüm kaldırılır. Autoritatif `novelty_frontier` ve tam deterministik
duplicate kapısı korunur.

## Continuous epoch ve token sözleşmesi

- Her epoch için Codex bütçesi 80.000, Claude bütçesi 100.000'dir.
- `STAGNATION_STOP`, controller token rollover ve S1 üretmeyen run yeni bounded
  epoch'a gider; normal rollover 10 saniye, no-progress cooldown 30 saniyedir.
- 160.000/200.000 kümülatif eşikleri durdurma değil görünür uyarı üretir.
- Prompt zarfı 16.000 karakter ve güvenlik payı 256 karakterdir;
  ekstra bütçe gereksiz geçmiş taşımak için kullanılmaz.
- Supervisor v2.1.8 state'indeki mevcut sayaçlar aynen korunur ve hiçbir epoch'ta sıfırlanmaz.
- Prompt zarfı/kompaksiyon kaynaklı recoverable durumlar
  `ORCHESTRATION_ROLLOVER` olarak 30 saniye içinde yeni epoch'a gider.
- Repo mutation, integrity/leakage, backtest güvenlik hatası, bilinmeyen state ve
  `TARGET_FOUND` gerçek hard-pause olarak kalır.

## Değişmeyen güvenlik sınırları

- `research_mode=offline`
- `trading_actions=false`
- `exchange_api_access=false`
- Emir, paper/live trading, S5/S6, deploy, Docker ve Git mutation yoktur.
- Claude tools/MCP/skills kapalıdır; worker network ve repo mutation fail-closed'dur.
- Frozen baseline, negative control, S1 kabul ölçütleri ve S2–S4 kapıları zayıflatılmaz.
- `TARGET_FOUND`, bilinmeyen state, integrity/leakage ve backtest hatası hard-pause üretir.
- Manuel `STOP_SUPERVISOR` her cooldown ve epoch sınırında önceliklidir.

## Sürümleme

v2.0.2–v2.0.16 immutable kalır. v2.0.17 ayrı release olarak kurulur.
Supervisor sözleşmesi v2.1.8'dır.
