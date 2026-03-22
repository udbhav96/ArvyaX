def decision_engine(predicted_state, intensity, stress_level, energy_level, time_of_day):
    #Decision Engine: decides WHAT to do and WHEN
    


    # WHAT TO DO
    # High stress + overwhelmed/restless → calming activities
    if predicted_state == 3:  # overwhelmed
        if intensity >= 3:
            what = 'box_breathing'
        else:
            what = 'grounding'

    elif predicted_state == 1:  # restless
        if stress_level >= 7:
            what = 'box_breathing'
        elif energy_level >= 7:
            what = 'movement'
        else:
            what = 'journaling'

    elif predicted_state == 0:  # mixed
        if stress_level >= 6:
            what = 'grounding'
        else:
            what = 'journaling'

    elif predicted_state == 4:  # calm
        if energy_level >= 6:
            what = 'deep_work'
        else:
            what = 'light_planning'

    elif predicted_state == 5:  # focused
        what = 'deep_work'

    elif predicted_state == 2:  # neutral
        if energy_level <= 3:
            what = 'rest'
        elif stress_level >= 6:
            what = 'sound_therapy'
        else:
            what = 'light_planning'

    else:
        what = 'journaling'  # fallback

    # WHEN TO DO 
    # Urgent if overwhelmed/restless at high intensity
    if predicted_state in [3, 1] and intensity >= 3:
        when = 'now'

    elif predicted_state in [3, 1] and intensity < 3:
        when = 'within_15_min'

    elif predicted_state == 0:  # mixed — not urgent
        when = 'within_15_min'

    elif predicted_state == 5:  # focused — schedule deep work smartly
        if time_of_day in [0, 1]:    # early morning / morning
            when = 'now'
        elif time_of_day == 2:       # afternoon
            when = 'now'
        else:                        # evening/night — don't push deep work
            when = 'tomorrow_morning'

    elif predicted_state == 4:  # calm
        if time_of_day == 4:         # night
            when = 'tonight'
        else:
            when = 'later_today'

    elif predicted_state == 2:  # neutral
        if time_of_day == 4:
            when = 'tonight'
        elif energy_level <= 3:
            when = 'now'
        else:
            when = 'later_today'

    else:
        when = 'later_today'  # fallback

    return what, when