# Wormhole (Einstein-Rosen Bridge)

Welcome to space! Run `./start.sh` to embark on your journey.
Run `./start.sh`

```
I. Make sure Dr.Rosen is alive.

    YOU -- VER (x05) -------------> ROSEN
    YOU -- NMETHODS (1) ----------> ROSEN
    YOU -- METHODS (1-255) -------> ROSEN
    YOU <------------- VER (x05) -- ROSEN
    YOU <---------- METHOD (x00) -- ROSEN
    YOU -- VER (x05) -------------> ROSEN
    YOU -- CMD (x01/x02/x03) -----> ROSEN

II. Dr.Rosen will then make sure that Dr.Einstein is alive.

                                    ROSEN -- SECRET ("Minkowski") ---> EINSTEIN
                                    ROSEN <------------- REP (0x00) -- EINSTEIN
    YOU <------------- RSV (x00) -- ROSEN

III. You tell Dr.Rosen about the mysterious man, he'll repeat your words to Dr.Einstein.

    YOU -- ATYP (x01/x03/x04) ----> ROSEN -- ATYP (x01/x03/x04) -----> EINSTEIN
    YOU -- DST.ADDR (N) ----------> ROSEN -- DST.ADDR (N) -----------> EINSTEIN
    YOU -- DST.PORT (2) ----------> ROSEN -- DST.PORT (2) -----------> EINSTEIN

IV. Dr.Einstein is the one to make the first contact.
                                                                       EINSTEIN -- ？
V. Dr.Rosen will let you know when he succeeds.

                                    ROSEN <---------- REP (x00/x0X) -- EINSTEIN
    YOU <------------- VER (x05) -- ROSEN
    YOU <--------- REP (x00/x0X) -- ROSEN
    YOU <------------- RSV (x00) -- ROSEN
    YOU <------------ ATYP (x01) -- ROSEN
    YOU <---------- BND.ADDR (4) -- ROSEN <----------- BND.ADDR (4) -- EINSTEIN
    YOU <-----------BND.PORT (2) -- ROSEN <----------- BND.PORT (2) -- EINSTEIN
```
