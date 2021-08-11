# Wormhole (Einstein-Rosen Bridge)

Welcome to space! Run `./start.sh` to embark on your journey.
Run `./start.sh`

```
    YOU ---- VER (x05) ----------->> R
    YOU ---- NMETHODS (1) -------->> R
    YOU ---- METHODS (1-255) ----->> R
    YOU <<-- VER (x05) ------------- R
    YOU <<-- METHOD (x00) ---------- R
                                     |
                              [if successful]
                                     | 
    YOU ---- VER (x05) ----------->> R
    YOU ---- CMD (x01/x02/x03) --->> R
                                     R ---- SECRET ("Minkowski") -->> E
                                     R <<-- REP (0x00) -------------- E
                                     |
                              [if successful]
                                     |
    YOU ---- RSV (x00) ----------->> R
    YOU ---- ATYP (x01/x03/x04) -->> R ---- ATYP (x01/x03/x04) ---->> E
    YOU ---- DST.ADDR (N) -------->> R ---- DST.ADDR (N) ---------->> E
    YOU ---- DST.PORT (2) -------->> R ---- DST.PORT (2) ---------->> E
                                                                      E <<-- [handshake] -->> ? 
    YOU <<-- VER (x05) ------------- R <<-- REP (x00/x0X) ----------- E
    YOU <<-- REP (x00/x0X) --------- R
    YOU <<-- RSV (x00) ------------- R
    YOU <<-- ATYP (x01) ------------ R
    YOU <<-- BND.ADDR (4) ---------- R <<-- BND.ADDR (4) ------------ E
    YOU <<-- BND.PORT (2) ---------- R <<-- BND.PORT (2) ------------ E
```
