def setup():
    from functions import P
    
    # -------------------------------------------------------------------------
    # Modifiable values 
    # -------------------------------------------------------------------------
   
    # -------------------------------------------------------------------------
    # i_SIPM measurement ------------------------------------------------------
    
    i_cc_sipm      = 18*P('m')
    v_cc_sipm      = 30.5
    
    i_rang_sipm    = 'AUTO'
    v_rang_sipm    = 'AUTO'
    
    v_level_sipm   = 0
    
    # -------------------------------------------------------------------------
    # i_LED measurement -------------------------------------------------------
    
    i_cc_led       = 5*P('m')
    v_cc_led       = 3
    
    i_rang_led     = 10*P('m')
    v_rang_led     = 20 #6 for k 2602B in CAC
	
	# -------------------------------------------------------------------------
	# ------------------------------------------------------------------------- 
    
    return_sweep   = 1
	
    # number of measurements
    
    N			       = 100.0

    points         = 100          # measurements per point in curve, 100 for NPLC = 1
	
    delay		    = 10*P('m')
    
    curves         = 1

   
    # -------------------------------------------------------------------------
    # End of setup
    # -------------------------------------------------------------------------

    
    return [i_cc_sipm,
            v_cc_sipm,
            i_rang_sipm,
            v_rang_sipm,
            v_level_sipm,
            i_cc_led,
            v_cc_led,
            i_rang_led,
            v_rang_led,
            return_sweep,
            N,
            points,
            delay,
            curves]