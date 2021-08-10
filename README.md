# Wormhole (Einstein-Rosen Bridge)

Welcome to space! Run `./start.sh` to embark on your journey.
Run `./start.sh`

```
    YOU ---- 1. VER (x05) ----------->> R
    YOU ---- 1. NMETHODS (1) -------->> R
    YOU ---- 1. METHODS (1-255) ----->> R
    YOU <<-- 2. VER (x05) ----------->> R
    YOU <<-- 2. METHOD (x00) -------->> R
    YOU ---- 3. VER (x05) ----------->> R
    YOU ---- 3. CMD (x01/x02/x03) --->> R
                                        R ---- SECRET ("Minkowski") -->> E
                                        R <<-- REP (0x00) -------------- E
    YOU <<-- 4. RSV (x00) ------------- R
    YOU ---- 3. ATYP (x01/x03/x04) -->> R ---- ATYP (x01/x03/x04) ---->> E
    YOU ---- 3. DST.ADDR (N) -------->> R ---- DST.ADDR (N) ---------->> E
    YOU ---- 3. DST.PORT (2) -------->> R ---- DST.PORT (2) ---------->> E
                                                                         E -- ？
                                        R <<-- REP (x00/x0X) ----------- E
    YOU <<-- 4. VER (x05) ------------- R
    YOU <<-- 4. REP (x00/x0X) --------- R
    YOU <<-- 4. RSV (x00) ------------- R
    YOU <<-- 4. ATYP (x01) ------------ R
    YOU <<-- 4. BND.ADDR (4) ---------- R <<-- BND.ADDR (4) ------------ E
    YOU <<-- 4. BND.PORT (2) ---------- R <<-- BND.PORT (2) ------------ E
```
