# Supportive message
import random
def generate_message(state, intensity, what, when):
    messages = {
        'overwhelmed': [
            f"You're carrying a lot right now — that's okay. Take a breath and try {what} {when}. One step at a time.",
            f"Feeling overwhelmed is valid. Let's slow things down with {what} {when}. You don't have to solve everything today.",
        ],
        'restless': [
            f"Your mind seems restless right now. A quick {what} {when} can help settle the noise.",
            f"Can't seem to slow down? Try {what} {when} — it'll help you reset.",
        ],
        'calm': [
            f"You're in a good headspace. Great time to channel that into {what} {when}.",
            f"Feeling calm is a gift — use it well. {what.replace('_',' ').title()} {when} sounds like a great move.",
        ],
        'focused': [
            f"You're sharp and ready. Lock in with {what} {when} — this is your window.",
            f"Focus mode activated. Best time for {what} is {when} — don't waste it.",
        ],
        'mixed': [
            f"Feeling mixed is normal — you're human. Start with {what} {when} to find some clarity.",
            f"When things feel conflicted, small steps help. Try {what} {when} to ground yourself.",
        ],
        'neutral': [
            f"Things feel quiet right now. Use this window for {what} {when} before the day picks up.",
            f"Neutral is a good place to plan from. {what.replace('_',' ').title()} {when} is a solid next step.",
        ],
    }
    options = messages.get(state, [f"Try {what} {when} to move toward a better state."])
    return random.choice(options)

