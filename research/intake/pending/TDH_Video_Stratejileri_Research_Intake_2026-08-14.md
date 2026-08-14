# TDH Research Intake — 9.000+ Strateji Testi Videosundan Çıkarılan Hipotezler

**Hazırlanma tarihi:** 2026-08-14  
**Hedef sistem:** TDH Strategy Lab / S1 offline araştırma  
**Kaynak video:** [Claude Tested Over 9,000 Trading Strategies (Here's What Works)](https://www.youtube.com/watch?v=nLQhKkjkuWI)  
**Transcript aracı:** [NoteGPT YouTube Transcript Generator](https://notegpt.io/youtube-transcript-generator)  
**Belge türü:** Uygulanabilir araştırma devri; sonuç raporu değildir.

---

## 1. Bu dosyanın diğer TDH oturumuna talimatı

Bu belgeyi alan oturum aşağıdaki sırayı izlemelidir:

1. TDH'nin güncel supervisor, aktif run, son mühürlü sürüm, staging sürümü, aile registry'si ve yürütme adaptörünü yeniden keşfet.
2. Bu belgedeki video bulgularını **kanıtlanmış kripto-futures edge'i değil, araştırma önceliği sağlayan hipotezler** olarak kullan.
3. Güncel mühürlü release'i hiçbir koşulda yerinde değiştirme. Değişiklik gerekiyorsa en son doğrulanmış release'den yeni staging sürümü üret.
4. Önce gerekli strateji ailelerini bounded schema, baseline ve negatif kontrol ile registry'ye ekle; serbest biçimli LLM strateji kodu çalıştırma.
5. En az maliyetli ve en yüksek bilgi kazançlı S1 deneyini başlat.
6. S1 geçmeden S2–S4, paper/live trading, S6 veya bot deployment'a geçme.
7. Bir backtest gerçekten başlamadan “eklendi/çalışıyor” deme. `run_id`, `experiment_id`, dataset/protocol hash'leri ve evaluator çıktısı ile kanıtla.

---

## 2. Değiştirilemez güvenlik ve araştırma kontratı

```yaml
research_mode: offline
trading_actions: false
exchange_api_access: false
live_trading: forbidden
paper_trading: forbidden
private_api_or_credentials: forbidden
s6_work: forbidden
s2_s3_s4_before_s1_pass: forbidden
```

### Zorunlu S1 hedefleri

Tüm kapılar birlikte geçilmelidir; ağırlıklı skorla bir başarısızlık diğerine karşı takas edilemez.

| Metrik | Zorunlu eşik |
|---|---:|
| Net win rate | ≥ %50 |
| Gerçekleşmiş reward/risk | ≥ 2.0 |
| Maksimum portföy drawdown | ≤ %10 |
| Maliyet sonrası expectancy | Pozitif |
| Profit factor | > 1.0 |
| Baseline karşılaştırması | Aday baseline'ı geçmeli |
| Negatif kontrol | Aday negatif kontrolü geçmeli |
| Kronolojik sağlamlık | Tüm temel WFO/OOS fold'larında korunmalı |
| Kullanıcının işlem sıklığı hedefi | Hafta içi ortalama ≥ 1 işlem/gün; ayrı raporlanmalı |

İşlem sıklığı hedefi diğer kalite kapılarını gevşetmek için kullanılamaz. Yüksek zaman aralığında işlem sayısı yetersiz kalırsa önce çoklu-varlık havuzu ve look-ahead-safe multi-timeframe tasarım denenmeli; sırf işlem sayısını yükseltmek için 1m gürültüsüne inilmemelidir.

---

## 3. Transcript bütünlüğü ve videonun gerçek kapsamı

Transcript internet tabanlı araçla çıkarıldı ve incelendi:

- 46 zaman damgalı ve sıralı bölüm bulundu.
- İlk bölüm `00:00`, son bölüm yaklaşık `19:25`; video yaklaşık 20 dakika.
- Bölümler arasında belirgin boşluk veya ters zaman damgası görülmedi.
- Tam transcript telif nedeniyle bu dosyaya kopyalanmadı; araştırma açısından gerekli iddialar ve zaman bağlantıları aşağıdadır.

### Kritik kapsam sınırı

Videodaki araştırma yaklaşık 15 yıllık **günlük barlar**, yaklaşık 30 likit varlık ve 9.000'den fazla strateji testi anlatıyor. Evren ETF, hisse, sektör, altın, petrol, tahvil ve bazı kriptoları içeriyor. Konuşmacı bunun intraday, futures veya options araştırması olmadığını açıkça belirtiyor.

Sonuç: Video, TDH kripto perpetual-futures sistemi için **doğrudan performans kanıtı değildir**. Yalnızca hangi ailelerin önce ve nasıl falsifiye edilmesi gerektiğini yönlendiren dış araştırma önceliğidir.

---

## 4. Videodan çıkarılan sağlam bulgular

| Bulgu | Video bağlantısı | TDH yorumu |
|---|---|---|
| Geniş evrende ortalama olarak ayakta kalan temel aile mean reversion oldu. | [02:14](https://youtu.be/nLQhKkjkuWI?t=134) | Naked trend ailesini sürekli mikro-optimize etmek yerine mean-reversion mekanizmasına öncelik ver. |
| Stratejiler walk-forward ve OOS filtrelerinden geçirildi. | [02:36](https://youtu.be/nLQhKkjkuWI?t=156) | Tek TradingView backtesti veya tek iyi pencere kabul edilemez. |
| In-sample güçlü stratejilerin yalnızca yaklaşık %44'ü OOS'ta güçlü kaldı. | [05:09](https://youtu.be/nLQhKkjkuWI?t=309) | Overfit ve çoklu test düzeltmesi ana risk olmalı. |
| Mean reversion çıplak halde ortalama pozitif; trend/momentum daha durumsal çıktı. | [07:17](https://youtu.be/nLQhKkjkuWI?t=437) | Trend yalnızca uygun rejim kapısıyla denenmeli. |
| 500 bootstrap yeniden örneklemesi kullanıldı; bazı cazip momentum örnekleri ağır drawdown üretti. | [08:17](https://youtu.be/nLQhKkjkuWI?t=497) | Bootstrap/stress test zorunlu; ortalama Sharpe yeterli değil. |
| RSI mean reversion 20, Keltner reversion 18 farklı ticker'da ayakta kaldı. | [11:30](https://youtu.be/nLQhKkjkuWI?t=690) | İlk iki mean-reversion adayı RSI ve Keltner olmalı. |
| Cross-sectional momentum, basit tek-varlık momentumundan daha iyi göründü. | [13:31](https://youtu.be/nLQhKkjkuWI?t=811) | Senkron çoklu-varlık verisi varsa üçüncü öncelikli aile. |
| Önerilen gerçek sistem: base edge + risk sizing + bağımsız sinyaller + regime gate. | [14:23](https://youtu.be/nLQhKkjkuWI?t=863) | Katmanlar tek tek ve birincil değişiklik kuralıyla doğrulanmalı. |
| Trend/bull rejiminde momentum; choppy/range rejiminde mean reversion öneriliyor. | [15:14](https://youtu.be/nLQhKkjkuWI?t=914) | İlk rejim kapısı deterministik olmalı; HMM sonradan karşılaştırılmalı. |
| Parametre hassasiyeti, maliyetler, multiple testing, bootstrap ve rejim kontrolleri birlikte öneriliyor. | [17:22](https://youtu.be/nLQhKkjkuWI?t=1042) | TDH'nin robust evaluator kontratıyla uyumlu. |

---

## 5. TDH öncelik sırası

### Öncelik 1 — `RSI_GATED_REVERSION`

**Tez:** Kısa dönem aşırı hareket, düşük-trend/yatay rejimde kısmen geri döner. RSI tek başına değil, rejim kapısıyla kullanılır.

**Gerekli veri:** Yalnızca look-ahead-safe OHLCV ve takvimsel perpetual funding/maliyet verisi.  
**İlk uygun evren:** Veri preflight'ını geçen BTCUSDT, ETHUSDT ve SOLUSDT.  
**İlk timeframe:** 15m. 1h/4h yalnızca canonical veri ve yeterli işlem sayısı varsa.  
**1m:** Registry/data kontratı açıkça uygun hale gelmeden kullanma.

#### Bounded schema

```yaml
family_id: RSI_GATED_REVERSION
rsi_period: [14, 21]
long_threshold: [20, 25, 30]
short_threshold: [70, 75, 80]
adx_period: [14]
adx_max: [20, 25]
atr_period: [14]
stop_atr: [1.0, 1.5]
target_r_multiple: [2.0]
max_holding_bars_15m: [12, 24, 48]
feature_timing: closed_bar_only
```

Threshold çiftleri simetrik olmalı (`20/80`, `25/75`, `30/70`). İlk sweep'te tüm kartezyen çarpımı çalıştırma. En az sekiz bağımsız fakat nedensel olarak yorumlanabilir konfigürasyonla aile ceiling'i araştır.

#### Aday, baseline ve negatif kontrol

- **Aday:** RSI extreme + `ADX <= adx_max`; 1R stop ve sabit 2R target; maliyet/funding dahil.
- **Baseline:** Aynı RSI, risk ve exit; ADX rejim kapısı yok.
- **Negatif kontrol:** Aynı koşullarda sinyal yönü ters çevrilmiş; oversold'da short, overbought'ta long.

İlk deneyin tek birincil değişikliği `regime_gate: none → ADX_LOW_TREND` olmalıdır. RSI period, threshold, stop ve holding süresi aynı deneyde birlikte değiştirilmemelidir.

#### Falsifikasyon

Aşağıdakilerden biri varsa hipotez başarısız sayılır:

- Aday baseline'ı ve negatif kontrolü robust olarak geçmiyor.
- Worst-fold expectancy ≤ 0.
- Aday yalnızca tek coin veya tek volatility rejiminde pozitif.
- Gerçekleşmiş R/R 2.0 altına kalıcı biçimde çöküyor.
- ADX filtresi yalnızca işlemleri azaltıyor, expectancy/WR/DD iyileştirmiyor.
- Sekiz bağımsız konfigürasyondan sonra `SIGNAL_PRECISION_CEILING`, `PAYOFF_FAMILY_CEILING`, `RISK_REGIME_FAILURE` veya `NO_INCREMENTAL_FAMILY_EDGE` oluşuyor.

---

### Öncelik 2 — `KELTNER_REVERSION`

**Tez:** Düşük-trend rejiminde Keltner kanalının dışına taşan fiyatın koşullu ortalamaya dönüş olasılığı vardır.

Bu aile videoda öne çıkıyor fakat önceki TDH durum görüntüsünde çalıştırılabilir family registry/adapter'da bulunmuyordu. Serbest kodla çalıştırılmamalı; önce resmi registry kaydı, bounded schema, adapter, tests ve negative control eklenmelidir.

#### Bounded schema

```yaml
family_id: KELTNER_REVERSION
ema_period: [20, 40]
atr_period: [14, 20]
band_atr_multiplier: [1.5, 2.0, 2.5]
adx_period: [14]
adx_max: [20, 25]
stop_extra_atr: [0.5, 1.0]
minimum_target_r: [2.0]
max_holding_bars_15m: [12, 24, 48]
feature_timing: closed_bar_only
```

#### Giriş ve çıkış semantiği

- Long: kapanmış bar alt Keltner bandının dışında ve düşük-trend kapısı açık.
- Short: kapanmış bar üst Keltner bandının dışında ve düşük-trend kapısı açık.
- Hedef: kanal orta çizgisine dönüş.
- Bir işlem yalnızca giriş anında orta çizgiye mesafe, tanımlı stop mesafesinin en az 2 katıysa uygundur.
- Stop, dış banttan bounded ATR mesafesiyle tanımlanır.
- Hedefe veya stopa ulaşmayan pozisyon bounded time-stop ile kapanır ve gerçekleşmiş R/R dürüstçe hesaplanır.

#### Kontroller

- **Baseline:** Aynı Keltner fade sinyali, ADX kapısı olmadan.
- **Negatif kontrol:** Dış banda taşmayı mean reversion yerine breakout continuation yönünde işlem yapan ters mekanizma.

#### İlk birincil değişiklik

`regime_gate: none → ADX_LOW_TREND`. Kanal periyodu ve band multiplier sabit tutulur. Aday gate'siz baseline'ı geçerse sonraki deneyde band genişliği ayrı olarak test edilebilir.

#### Falsifikasyon

- Mean-line target'a göre uygun 2R fırsatları işlem sıklığı hedefini karşılamayacak kadar azsa.
- Maliyet ve funding sonrası expectancy negatife dönüyorsa.
- Breakout negatif kontrolü adayı geçiyorsa; bu durumda pazar seçilen rejimde reversion değil continuation gösteriyor olabilir.
- Parametre komşuluğu geniş plateau yerine tek nokta optimumu üretiyorsa.

---

### Öncelik 3 — `CROSS_SECTION_MOM`

**Tez:** Tek-varlık zaman serisi momentumundan ziyade, aynı anda işlem gören likit kripto perpetual'larını göreli performansa göre sıralamak daha istikrarlı bir momentum sinyali üretebilir.

**Uygunluk ön koşulları:** Semboller UTC bakımından senkron olmalı; eksik bar, listing bias, survivorship bias ve likidite elemesi deterministik olmalı. Tek bir güçlü coin toplam performansı maskeleyemez.

#### Bounded schema

```yaml
family_id: CROSS_SECTION_MOM
timeframe: [1h, 4h]
ranking_lookback_bars: [20, 60, 120]
top_quantile: [0.2, 0.33]
bottom_quantile: [0.2, 0.33]
rebalance_bars: [4, 8, 24]
position_sizing: [equal_weight, inverse_vol]
position_stop_r: [1.0]
position_target_r: [2.0]
feature_timing: closed_bar_only
```

#### Kontroller

- **Baseline:** Aynı evren ve yeniden dengeleme; tek-varlık return-sign momentum veya eşit ağırlıklı buy-and-hold-perp karşılaştırması, protokolde hangisi immutable olarak kayıtlıysa.
- **Negatif kontrol:** Rank sırasını ters çevir; güçlüleri short, zayıfları long.

Bu aile TDH'nin pozisyon-seviyesi yapısal 2R kontratını ifade edemiyorsa **bloklanmalı**, R/R kapısı gevşetilmemelidir.

---

### Öncelik 4 — Deterministik rejim filtresi ve MTF katmanı

Videoda HMM öneriliyor; fakat ilk deney için HMM fazla serbestlik ve overfit riski getirir. İlk rejim katmanı açıklanabilir ve deterministik olmalıdır.

```yaml
range_regime:
  adx_max: [20, 25]
  realized_vol_percentile_max: [80, 90]
trend_regime:
  adx_min: [25, 30]
  ema_slope_direction_required: true
```

İlk multi-timeframe hipotezi:

- 15m giriş sinyali.
- Yalnızca tamamlanmış 1h bardan hesaplanan rejim kapısı.
- Baseline aynı 15m sinyali, 1h filtresi olmadan.
- Negatif kontrol 1h rejim etiketini ters uygular.
- Birincil değişiklik yalnızca `timeframe_regime_gate: none → 1h` olur.

MTF katmanı, temel mean-reversion ailesi en az near-miss göstermeden eklenmemelidir. Aksi halde hangi katmanın edge ürettiği bilinemez.

---

## 6. İlk S1 deney paketi

### Paket A — En ucuz ayırt edici test

```yaml
experiment_family: RSI_GATED_REVERSION
symbols: [BTCUSDT, ETHUSDT, SOLUSDT]
timeframe: 15m
candidate: RSI_14_25_75_ADX_MAX_20
baseline: same_without_ADX_gate
negative_control: inverted_signal_same_cost_and_risk
stop: 1R
target: 2R
max_holding_bars: 24
primary_change: add_low_trend_regime_gate
```

Bu çekirdek karşılaştırma tüm semboller ve aynı WFO fold'ları üzerinde çalıştırıldıktan sonra, yalnızca sonuç ayrıştırıcıysa yedi ek bağımsız konfigürasyonla family-ceiling teşhisi tamamlanmalıdır. İlk turda dev grid search yapılmamalıdır.

### Paket B — RSI mekanizması near-miss veya pass gösterirse

- RSI period `14 → 21` tek değişiklik.
- Threshold `25/75 → 20/80` tek değişiklik.
- ADX cap `20 → 25` tek değişiklik.
- 15m giriş + kapalı 1h rejim filtresi tek değişiklik.

Her adımda aday, baseline ve negatif kontrol aynı immutable dataset, costs ve fold'larla yeniden çalıştırılmalıdır.

### Paket C — RSI ailesi ceiling gösterirse

RSI'yi kozmetik olarak mikro-tune etmeyi bırak ve `KELTNER_REVERSION` ailesine geç. Bu değişiklik farklı bir mekanizma olarak ledger'a yazılmalıdır.

### Paket D — Mean reversion ailelerinden sonra

Senkron çoklu-varlık preflight'ı geçiyorsa `CROSS_SECTION_MOM` çalıştır. Trend/momentum ailesini yalnızca rejim koşullu ve kontrol karşılaştırmalı test et; önceki naked trend başarısızlıklarını tekrarlama.

---

## 7. Zorunlu veri ve değerlendirme protokolü

Her deney öncesi aşağıdaki bilgiler hash'lenmeli ve fail-closed doğrulanmalıdır:

- Dataset kaynağı/sürümü ve canonical path.
- Sembol, taban timeframe, UTC başlangıç/bitiş.
- Satır sayısı, monotonic timestamp, duplicate ve missing bars.
- Resampling: `label=right`, `closed=right`, incomplete bar drop; OHLCV=`first,max,min,last,sum`.
- Bütün feature'lar closed-bar-only; look-ahead yok.
- Dataset, partition ve protocol hash'leri.

### WFO/OOS

- Kronolojik rolling walk-forward kullanılmalı.
- Overlap varsa purge/embargo uygulanmalı.
- Tuning dışında mühürlü OOS/true-forward segment tutulmalı.
- Aynı konfigürasyon bütün fold'larda tek `strategy_config_sha256` altında toplanmalı.
- Bull, bear, sideways, high-vol ve low-vol rejimleri ayrı raporlanmalı.
- Coin bazlı ve pooled sonuçlar birlikte gösterilmeli.
- En az 300 toplam işlem hedeflenmeli; ancak az işlem veri eksikliğini gizlemek için fold'lar birleştirilmemeli.

### Gerçekçi maliyetler

- Maker/taker fee.
- Bid/ask spread.
- Muhafazakâr slippage.
- Perpetual funding.
- Margin ve liquidation-aware risk.
- Kapasite/likidite filtresi.

Candle OHLCV ile order-book, queue position, market making veya latency edge'i iddia edilmemelidir.

### Robust karar sırası

1. Bütün S1 kapıları geçti mi?
2. Aday baseline ve negatif kontrolü geçti mi; bütün temel fold'lar pozitif mi?
3. Kaç hedef ihlali var?
4. Worst-fold expectancy nedir?
5. Worst-fold DD nedir?
6. Median PF ve WR marjı nedir?

Tek iyi pencere `FRAGILE` olarak etiketlenmeli. Toplam/ortalama PnL, katastrofik bir fold'u telafi edemez.

### Çoklu test ve bootstrap

- Her test edilen hipotez denominator'a kaydedilmeli.
- Parametre komşuluk kararlılığı aranmalı.
- En az 500 bootstrap/stress yeniden örneklemesi önerilir.
- White/SPA, false-discovery veya deflated metric türü önceden ilan edilmiş bir düzeltme kullanılmalı.
- Video/literatür skoru yalnızca prior'dır; exact parametre kanıtı değildir.

---

## 8. Önceki TDH durumundan negatif hafıza

Bu bölüm yalnızca 2026-08-14 tarihli önceki oturum snapshot'ıdır; yeni oturum canonical raw artifacts ile tekrar doğrulamalıdır.

- `MA_TREND` ailesinin son 1d adaylarında negatif expectancy, yaklaşık %20–36 WR, gerçekleşmiş R/R < 1 ve çok düşük hafta içi işlem sıklığı görüldü.
- `SUPPORT_RES_BREAK` 12h adayları yaklaşık 3–7 işlem üretti; WR sıfıra yakın/sıfır ve expectancy negatifti.
- Son tur verdict'i `REVISE`, survivor sayısı sıfırdı.
- Bu kanıt, naked trend ve support/resistance breakout ailelerinde kozmetik tuning yerine farklı bir mekanizma denenmesini destekliyor.

Bu snapshot yeni sonuçların yerine geçmez. Hash'li experiment ledger'da aynı konfigürasyonlar varsa duplicate olarak reddedilmelidir.

---

## 9. Bilinen entegrasyon durumu ve yeni oturumun çözmesi gereken engel

Önceki oturumda görülen durum:

- `RSI_GATED_REVERSION`, `BOLLINGER_REVERSION`, `CROSS_SECTION_MOM` ve `VOL_REGIME_GATE` atlas/deney kuyruğunda bulunuyordu.
- Fakat güncel yürütme adapter/registry'si RSI ve Keltner mean-reversion ailelerini çalıştırmıyordu.
- Son doğrulanan release `v2.0.50` idi ve değiştirilmedi.
- `v2.0.50 → v2.0.51` staging clone denemesi controller tarafında eski sabit nedeniyle `BLOCKED: clone source must be v2.0.20` mesajıyla engellendi.
- Supervisor offline araştırmada çalışıyordu; exchange erişimi ve trading actions kapalıydı.

### Yeni oturumun entegrasyon prosedürü

1. Bu bilgilerin hâlâ güncel olup olmadığını status ve filesystem/release kanıtıyla kontrol et.
2. Admin gate veya MCP action sürüm sabitlerini güncel **source release → next staging release** olacak şekilde güvenli biçimde ilerlet.
3. En son sealed release'in SHA256 ve preflight doğrulamasını yap.
4. Supervisor'ı kontrollü biçimde durdur/mask etmeden aktif release dosyalarını değiştirme.
5. Yeni staging'e registry card, bounded schema, adapter ve tests ekle.
6. Aşağıdaki testleri ekle:
   - unknown family fail-closed;
   - look-ahead koruması;
   - resampling timing;
   - candidate/baseline/negative-control eşit protokol;
   - costs/funding;
   - 2R ve DD gate;
   - duplicate/negative-memory;
   - oversized prompt fail-closed;
   - live/paper/exchange capability kesinlikle yok;
   - fragile winner ve catastrophic worst-fold reddi.
7. Registry validator ve bütün unit/integration testlerini çalıştır.
8. Preflight `PREFLIGHT_OK`, checksum ve sealed proof olmadan service switch yapma.
9. Yeni release çalıştıktan sonra yalnızca Paket A'yı başlat; ilk sonuç gelmeden geniş sweep açma.

---

## 10. Beklenen machine-facing deney çıktısı

Her fold için en az şu alanlar üretilmelidir:

```json
{
  "strategy_config_sha256": "64-lowercase-hex",
  "family_id": "RSI_GATED_REVERSION",
  "experiment_id": "stable-id",
  "window_id": "wfo-001",
  "dataset_sha256": "64-lowercase-hex",
  "protocol_sha256": "64-lowercase-hex",
  "metrics": {
    "expectancy": 0.0,
    "profit_factor": 1.0,
    "win_rate": 0.5,
    "realized_rr": 2.0,
    "max_drawdown_pct": 10.0,
    "net_pnl": 0.0,
    "trade_count": 0,
    "weekday_trades_per_day": 0.0
  },
  "gates": {
    "s1_pass": false,
    "baseline_beaten": false,
    "negative_control_beaten": false,
    "all_core_folds_positive": false
  }
}
```

Tur sonunda tek bir canonical ledger satırı yazılmalı ve şu sınıflardan biriyle bitmelidir:

- `ACCEPTED`
- `REJECTED`
- `FRAGILE`
- `PAYOFF_FAMILY_CEILING`
- `SIGNAL_PRECISION_CEILING`
- `RISK_REGIME_FAILURE`
- `NO_INCREMENTAL_FAMILY_EDGE`

---

## 11. Diğer oturumdan istenecek kısa görev metni

Aşağıdaki metin bu dosyayla birlikte yeni TDH oturumuna verilebilir:

> Bu `.md` dosyasını TDH için yeni research intake olarak kullan. Önce güncel supervisor/release/registry/adapter durumunu doğrula; dosyadaki snapshot'ı körlemesine kabul etme. Offline ve S1-only kontratını koruyarak en son sealed release'den yeni staging üret, `RSI_GATED_REVERSION` ve `KELTNER_REVERSION` ailelerini bounded schema + baseline + negative control ile çalıştırılabilir hale getir. Önce yalnızca Paket A'nın en ucuz ayırt edici S1 testini başlat. Sonuçları tüm WFO fold'larında, maliyet/funding dahil, hash'li ve control karşılaştırmalı raporla. Canlı/paper trading, exchange erişimi, S6 veya S1 geçmeden S2–S4 kesinlikle yok.

---

## 12. Başarı tanımı

Bu araştırmanın başarısı “çok sayıda backtest” veya “bir yerde yüksek PnL” değildir. Başarı aşağıdakilerden biridir:

1. Bütün zorunlu kapıları ve kontrolleri robust olarak geçen, tekrar üretilebilir bir S1 adayı bulunur; veya
2. Aile dürüstçe falsifiye edilir, failure mechanism ve negative memory kaydedilir ve sonraki farklı mekanizma için bilgi kazanılır.

Başarısız strateji de düzgün falsifiye edilmişse değerli araştırma çıktısıdır. Hiçbir metrik veya sonuç uydurulmamalıdır.
