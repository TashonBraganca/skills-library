# Measured palette library

Every palette below was **measured from real design work**, not invented. Source: 138 Dribbble
shots scraped across the tags `minimal`, `editorial`, `typography`, `muted`, `dashboard`, each
k-means reduced to 6 dominant colours weighted by pixel area.

**106 of 138 were rejected.** What survived passes all three gates below.

## The colour law

Derived by measuring ten generated pages against one person's recorded like/dislike verdicts,
area-weighted over rendered pixels (not CSS hex counts — counting hex strings gave the wrong
answer and had to be discarded).

| Gate | Threshold | Why |
|---|---|---|
| Hue spread | **>= 17 degrees** | Liked pages measured 17.6-41.5 deg. Disliked measured 3.1-10.3 deg. A single hue tinting everything is what reads as cheap. |
| Median chroma | **30-53 %** | Liked measured 33-51 %. Disliked measured 56-87 %. Above ~55 % is the 'poppy' failure. |
| Text/ground contrast | **>= 4.5:1** | One rejected page was called simply 'can't read shit'. Non-negotiable. |

Two or three genuinely different hue families, each held quiet. Not one hue everywhere, and not neon.

Verify any palette with `scripts/measure_palette.py` before shipping. It exits non-zero on failure.

## The palettes

Ordered by number of distinct chromatic hues. `spread` = weighted hue dispersion in degrees;
`chroma` = median saturation of chromatic pixels; `contrast` = best text-on-ground pair in the palette.

### amber + green + blue + terracotta  ·  spread 65.4° · chroma 40.4% · contrast 5.18:1

| `#fee952` | `#527046` | `#fbf9ca` | `#9cb3de` | `#c39155` | `#feee54` |
|---|---|---|---|---|---|
| amber | green | amber | blue | terracotta | amber |

Text/ground pair: `#527046` on `#fbf9ca`

### teal + terracotta + blue  ·  spread 46.3° · chroma 33.5% · contrast 12.51:1

| `#87baa2` | `#e6d3c9` | `#687480` | `#454f64` | `#0f1333` | `#29304d` |
|---|---|---|---|---|---|
| teal | terracotta | blue | blue | blue | blue |

Text/ground pair: `#e6d3c9` on `#0f1333`

### teal + blue + amber  ·  spread 45.4° · chroma 31.0% · contrast 10.88:1

| `#cce6eb` | `#646c85` | `#262b3e` | `#3d496a` | `#ede927` | `#92a5c4` |
|---|---|---|---|---|---|
| teal | blue | blue | blue | amber | blue |

Text/ground pair: `#262b3e` on `#ede927`

### terracotta + amber  ·  spread 29.4° · chroma 40.9% · contrast 11.65:1

| `#d1ab7f` | `#e8cbac` | `#3e3222` | `#1d150b` | `#5d5748` | `#967c5f` |
|---|---|---|---|---|---|
| terracotta | terracotta | terracotta | terracotta | amber | terracotta |

Text/ground pair: `#e8cbac` on `#1d150b`

### red + teal + blue + amber  ·  spread 74.0° · chroma 50.4% · contrast 6.19:1

| `#f6f9fb` | `#e97f62` | `#1d6484` | `#bebfde` | `#7ab6e1` | `#f5d782` |
|---|---|---|---|---|---|
| paper | red | teal | blue | blue | amber |

Text/ground pair: `#f6f9fb` on `#1d6484`

### teal + amber  ·  spread 42.4° · chroma 38.1% · contrast 17.04:1

| `#1a2222` | `#0f1616` | `#79b7c8` | `#245559` | `#f5f7f8` | `#7f815b` |
|---|---|---|---|---|---|
| teal | teal | teal | teal | paper | amber |

Text/ground pair: `#0f1616` on `#f5f7f8`

### green + amber  ·  spread 37.3° · chroma 34.5% · contrast 11.18:1

| `#020302` | `#11160d` | `#273021` | `#4d533c` | `#81826c` | `#bbc1af` |
|---|---|---|---|---|---|
| green | green | green | green | amber | neutral |

Text/ground pair: `#020302` on `#bbc1af`

### green + red + blue + teal  ·  spread 78.9° · chroma 43.0% · contrast 15.8:1

| `#2f4f3c` | `#b85741` | `#1d1e23` | `#455f54` | `#f9f9f9` | `#a29f95` |
|---|---|---|---|---|---|
| green | red | blue | teal | paper | neutral |

Text/ground pair: `#1d1e23` on `#f9f9f9`

### red + green + terracotta  ·  spread 68.7° · chroma 45.0% · contrast 15.97:1

| `#9b756e` | `#1f1d1c` | `#4c735f` | `#e1ac68` | `#d1c5ab` | `#faf9f8` |
|---|---|---|---|---|---|
| red | ink | green | terracotta | terracotta | paper |

Text/ground pair: `#1f1d1c` on `#faf9f8`

### terracotta + teal  ·  spread 52.4° · chroma 40.6% · contrast 16.73:1

| `#181817` | `#9c6e5a` | `#6b827d` | `#cbb28a` | `#59493f` | `#f8f8f8` |
|---|---|---|---|---|---|
| ink | terracotta | teal | terracotta | terracotta | paper |

Text/ground pair: `#181817` on `#f8f8f8`

### red + terracotta + blue  ·  spread 20.0° · chroma 38.4% · contrast 9.75:1

| `#2b2c30` | `#292a2e` | `#f56666` | `#ecc59d` | `#634549` | `#222327` |
|---|---|---|---|---|---|
| neutral | neutral | red | terracotta | red | blue |

Text/ground pair: `#ecc59d` on `#222327`

### blue + terracotta  ·  spread 89.9° · chroma 46.2% · contrast 5.94:1

| `#f8f9f9` | `#50b6fa` | `#e5e7e7` | `#a2d1f2` | `#d4b687` | `#5c6164` |
|---|---|---|---|---|---|
| paper | blue | paper | blue | terracotta | neutral |

Text/ground pair: `#f8f9f9` on `#5c6164`

### green + terracotta  ·  spread 43.5° · chroma 40.7% · contrast 13.1:1

| `#f4efe9` | `#cfe09b` | `#342a23` | `#8d7158` | `#b2a99e` | `#fbf7f0` |
|---|---|---|---|---|---|
| paper | green | terracotta | terracotta | neutral | paper |

Text/ground pair: `#342a23` on `#fbf7f0`

### terracotta  ·  spread 43.4° · chroma 40.8% · contrast 17.93:1

| `#fcfcfc` | `#75797f` | `#e4d6cf` | `#19130f` | `#c8a38e` | `#804a32` |
|---|---|---|---|---|---|
| paper | neutral | paper | terracotta | terracotta | terracotta |

Text/ground pair: `#fcfcfc` on `#19130f`

### terracotta + teal  ·  spread 41.6° · chroma 50.5% · contrast 7.25:1

| `#fefefe` | `#f7f5f1` | `#f2e3d7` | `#f6a85d` | `#2e5c6e` | `#83c1ba` |
|---|---|---|---|---|---|
| paper | paper | paper | terracotta | teal | teal |

Text/ground pair: `#fefefe` on `#2e5c6e`

### blue + red  ·  spread 26.1° · chroma 37.9% · contrast 10.96:1

| `#374858` | `#bebebe` | `#fdfdfd` | `#a58381` | `#2d3d4c` | `#dadadc` |
|---|---|---|---|---|---|
| blue | neutral | paper | red | blue | paper |

Text/ground pair: `#fdfdfd` on `#2d3d4c`

### red + terracotta  ·  spread 26.0° · chroma 48.9% · contrast 15.38:1

| `#efebf1` | `#ebe5ec` | `#faf9fa` | `#2d1d17` | `#974e43` | `#c7aa8c` |
|---|---|---|---|---|---|
| paper | paper | paper | red | red | terracotta |

Text/ground pair: `#faf9fa` on `#2d1d17`

### amber + green  ·  spread 19.9° · chroma 51.9% · contrast 12.87:1

| `#f5ee69` | `#c5c3bf` | `#989995` | `#57594e` | `#c1b755` | `#232421` |
|---|---|---|---|---|---|
| amber | neutral | neutral | green | amber | ink |

Text/ground pair: `#f5ee69` on `#232421`

### terracotta + green  ·  spread 77.8° · chroma 43.5% · contrast 5.54:1

| `#eaeaeb` | `#fefefe` | `#f7f7f7` | `#fbfbfb` | `#c5b7ab` | `#606b5d` |
|---|---|---|---|---|---|
| paper | paper | paper | paper | terracotta | green |

Text/ground pair: `#fefefe` on `#606b5d`

### green + terracotta  ·  spread 63.4° · chroma 35.6% · contrast 17.42:1

| `#f0f0ef` | `#fefefe` | `#19191a` | `#435744` | `#a58160` | `#f7f7f7` |
|---|---|---|---|---|---|
| paper | paper | ink | green | terracotta | paper |

Text/ground pair: `#fefefe` on `#19191a`

### blue  ·  spread 51.9° · chroma 35.3% · contrast 4.94:1

| `#f7f7f7` | `#ebedf0` | `#c9c5c5` | `#93baf5` | `#4771ab` | `#fefefe` |
|---|---|---|---|---|---|
| paper | paper | neutral | blue | blue | paper |

Text/ground pair: `#4771ab` on `#fefefe`

### terracotta  ·  spread 35.4° · chroma 48.0% · contrast 7.02:1

| `#f7f6f6` | `#e7e7e6` | `#fcfcfc` | `#695342` | `#b99c8e` | `#f8f8f8` |
|---|---|---|---|---|---|
| paper | paper | paper | terracotta | terracotta | paper |

Text/ground pair: `#fcfcfc` on `#695342`

### teal  ·  spread 100.3° · chroma 39.3% · contrast 16.63:1

| `#bfc3cf` | `#f9fafa` | `#e4e3e4` | `#434d4d` | `#1a1a1b` | `#81807c` |
|---|---|---|---|---|---|
| neutral | paper | paper | teal | ink | neutral |

Text/ground pair: `#f9fafa` on `#1a1a1b`

### terracotta  ·  spread 80.7° · chroma 30.6% · contrast 17.92:1

| `#101010` | `#f2f2f2` | `#b9bdbc` | `#888a82` | `#544e46` | `#f8f8f8` |
|---|---|---|---|---|---|
| ink | paper | neutral | neutral | terracotta | paper |

Text/ground pair: `#101010` on `#f8f8f8`
