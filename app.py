import curses
import time
import random
import webbrowser
import textwrap
from curses import wrapper

# Fake Stock Tickers
TICKERS = ["APPL", "FTSE", "LHR", "JPM", "GSL", "BPL", "ARR"]

# Funny/Absurd News Headlines
NEWS_HEADLINES = [
    "BREAKING: Local Man Buys High, Sells Low; Surprised by Outcome.",
    "Computer Science Wizards buy high on Crypto.",
    "Very important bbg news headline",
    "Experts say: 'Invest in memes, not dreams.'",
]

# Fake Portfolio
FAKE_PORTFOLIO = {
    "ABC Inc.": {"qty": 6.1, "value": 1, "notes": "Guaranteed to grow to the sky. Maybe."},
    "BIG TECH": {"qty": 1, "value": 0.01, "notes": "Can't see it, but it's priceless."},
    "Stonks (AI)": {"qty": 42, "value": 999999.99,"notes": "Great for memes, bad for wallets."},
    "Crypto Bro": {"qty": 50, "value": 150000.00, "notes": "Better than actual currency, right?"},
}

# --- BALLOON GAME STATE ---
class BalloonGame:
    def __init__(self):
        self.reset_round()
        self.total_earnings = 0
        self.rounds_played = 0
        
    def reset_round(self):
        self.active = False
        self.pumps = 0
        self.max_pumps = random.randint(5, 30)
        self.current_earnings = 0
        self.burst = False
        self.redeemed = False

# --- END OF SETTINGS ---

def initialize_colors():
    """Initializes color pairs for the UI."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # Green
    curses.init_pair(2, curses.COLOR_RED, -1)    # Red
    curses.init_pair(3, curses.COLOR_YELLOW, -1) # Yellow
    curses.init_pair(4, curses.COLOR_CYAN, -1)   # Cyan
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED) # Error BG
    curses.init_pair(6, curses.COLOR_MAGENTA, -1) # Magenta for balloon


def draw_ui(stdscr, tickers_win, news_win, output_win, cmd_win):
    """Draws the static UI layout."""
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.bkgd(' ', curses.color_pair(4))
    stdscr.addstr(0, 0, " B L O O M B E R G ", curses.A_REVERSE)
    stdscr.addstr(0, w - len(" [TERMINAL] "), " [TERMINAL] ", curses.A_REVERSE)
    stdscr.refresh()
    
    # Tickers Box
    tickers_win.box()
    tickers_win.addstr(0, 2, " LIVE MARKET DATA ", curses.color_pair(3))
    
    # News Box
    news_win.box()
    news_win.addstr(0, 2, " WIRE SERVICE ", curses.color_pair(3))

    # Main Output Box
    output_win.box()
    output_win.addstr(0, 2, " CONSOLE ", curses.color_pair(3))
    
    # Command Box
    cmd_win.box()
    cmd_win.addstr(0, 2, " COMMAND ", curses.color_pair(3))

def update_tickers(win):
    """Updates the fake stock tickers with random data."""
    win.erase()
    win.box()
    win.addstr(0, 2, " LIVE MARKET DATA ", curses.color_pair(3))
    max_y, max_x = win.getmaxyx()
    
    for i, ticker in enumerate(TICKERS):
        if i + 1 >= max_y - 1:
            break
        
        price = random.uniform(5.0, 500.0)
        change = random.uniform(-20.0, 20.0)
        
        symbol, color = ("▲", 1) if change >= 0 else ("▼", 2)
        
        line = f" {ticker:<7} {price:8.2f} {symbol} {change:+.2f}"
        win.addstr(i + 1, 2, line, curses.color_pair(color))
    win.refresh()

def scroll_news(win, headlines, scroll_pos):
    """Scrolls the news headlines horizontally."""
    win.erase()
    win.box()
    win.addstr(0, 2, " BEST FAKEST NEWS ", curses.color_pair(3))
    _, max_x = win.getmaxyx()
    
    display_width = max_x - 4
    full_headline_text = "   |   ".join(headlines) + "   |   "
    
    # Loop the text
    start_index = scroll_pos % len(full_headline_text)
    
    # Create the text to display
    scrolling_text = (full_headline_text[start_index:] + full_headline_text[:start_index])[:display_width]
    
    win.addstr(1, 2, scrolling_text, curses.color_pair(3))
    win.refresh()
    return (scroll_pos + 1) % len(full_headline_text)


def draw_balloon(win, game):
    """Draws the balloon game interface."""
    if not game.active:
        return
    
    max_h, max_w = win.getmaxyx()
    
    # Clear area for balloon
    for i in range(1, max_h - 1):
        try:
            win.addstr(i, 2, " " * (max_w - 4))
        except:
            pass
    
    if game.burst:
        # Show burst animation
        burst_art = [
            "    * * *    ",
            "  *  POP!  * ",
            "    * * *    "
        ]
        start_y = max_h // 2 - 2
        for i, line in enumerate(burst_art):
            if start_y + i < max_h - 1:
                win.addstr(start_y + i, max_w // 2 - len(line) // 2, line, curses.color_pair(2) | curses.A_BOLD)
        
        win.addstr(max_h - 2, 2, f"BURST! Lost £{game.current_earnings:.2f}", curses.color_pair(2))
    
    elif game.redeemed:
        # Show success message
        win.addstr(max_h // 2, max_w // 2 - 10, "REDEEMED!", curses.color_pair(1) | curses.A_BOLD)
        win.addstr(max_h - 2, 2, f"Banked: £{game.current_earnings:.2f}", curses.color_pair(1))
    
    else:
        # Draw balloon based on pump count
        size = min(game.pumps, 15)
        
        # Simple balloon art that grows
        if size <= 3:
            balloon = ["  o  ", " o o ", "  |  "]
        elif size <= 7:
            balloon = ["  .-.  ", " ( o ) ", "  '-'  ", "   |   "]
        elif size <= 12:
            balloon = ["  .--.  ", " /    \\ ", "|  ()  |", " \\    / ", "  '--'  ", "    |   "]
        else:
            balloon = ["   .----.   ", "  /      \\  ", " |        | ", "|    ()    |", " |        | ", "  \\      /  ", "   '----'   ", "      |     "]
        
        start_y = max(1, (max_h - len(balloon)) // 2)
        color = curses.color_pair(6) if game.pumps < 20 else curses.color_pair(3)
        
        for i, line in enumerate(balloon):
            if start_y + i < max_h - 1:
                win.addstr(start_y + i, max_w // 2 - len(line) // 2, line, color | curses.A_BOLD)
        
        # Show stats
        win.addstr(max_h - 3, 2, f"Pumps: {game.pumps}/30 | Current: £{game.current_earnings:.2f}", curses.color_pair(1))
        win.addstr(max_h - 2, 2, f"SPACE to pump | R to redeem | Total: £{game.total_earnings:.2f}", curses.color_pair(4))


def process_command(cmd_str, output_win, game):
    """Processes user commands and displays output."""
    cmd_parts = cmd_str.upper().split()
    if not cmd_parts:
        return
    
    command = cmd_parts[0]
    args = cmd_parts[1:]

    if command == "HELP":
        add_message(output_win, "RUN EVERY COMMAND IN ORDER TO GET THE CLUE", 3)
        add_message(output_win, "--- AVAILABLE COMMANDS ---", 4)
        add_message(output_win, "HELP      - Displays this help message.")
        add_message(output_win, "NEWS      - Shows latest financial news.")
        add_message(output_win, "PORTFOLIO - Displays your current absurd holdings.")
        add_message(output_win, "BALLOON   - Start the balloon trading game!")
        add_message(output_win, "CLEAR     - Clears this message console.")
        add_message(output_win, "---", 4)

    elif command == "NEWS":
        add_message(output_win, "--- LATEST HEADLINES ---", 3)
        for headline in random.sample(NEWS_HEADLINES, min(4, len(NEWS_HEADLINES))):
            add_message(output_win, f"● {headline}")

    elif command == "PORTFOLIO":
        add_message(output_win, "--- PORTFOLIO OVERVIEW ---", 4)
        for item, data in FAKE_PORTFOLIO.items():
            add_message(output_win, f"{item}: Qty={data['qty']}, Value=${data['value']:,.2f}", 1)
            add_message(output_win, f"  └─ Notes: {data['notes']}", 3)

    elif command == "BALLOON":
        if not game.active:
            game.reset_round()
            game.active = True
            add_message(output_win, "BALLOON GAME STARTED! Press SPACE to pump, R to redeem!", 1)
            return "balloon_start"
        else:
            add_message(output_win, "Game already in progress!", 3)

    elif command == "CLEAR":
        return "clear"
    else:
        add_message(output_win, f"ERROR: Unknown command '{command}'. This incident will be reported.", 2)


# List to hold messages
message_log = []

def add_message(win, text, color=0):
    """Adds a message to the log and redraws the output window."""
    global message_log
    max_h, max_w = win.getmaxyx()
    width = max_w - 4
    
    # Wrap text
    wrapped_lines = textwrap.wrap(text, width)
    
    for line in wrapped_lines:
        message_log.append((line, color))
    
    # Keep log from getting too long
    max_lines = max_h - 2
    message_log = message_log[-max_lines:]
    
    redraw_output(win)
    
def redraw_output(win):
    """Redraws the output window from the message log."""
    win.erase()
    win.box()
    win.addstr(0, 2, " CONSOLE ", curses.color_pair(3))
    
    max_h, _ = win.getmaxyx()
    
    # Draw messages from the bottom up
    lines_to_draw = message_log[-(max_h - 2):]
    
    for i, (msg, color) in enumerate(lines_to_draw):
        win.addstr(i + 1, 2, msg, curses.color_pair(color))
    win.refresh()
    
def main(stdscr):
    """Main function to run the application."""
    initialize_colors()
    curses.curs_set(1)

    stdscr.clear()
    stdscr.nodelay(True) # Non-blocking input
    stdscr.keypad(True) # Enable keypad for special keys

    h, w = stdscr.getmaxyx()

    # Define window sizes
    tickers_win = curses.newwin(h - 5, 30, 1, 1)
    news_win = curses.newwin(3, w - 2, h - 4, 1)
    output_win = curses.newwin(h - 8, w - 32, 1, 31)
    cmd_win = curses.newwin(3, w - 32, h - 7, 31)

    # Initial draw
    draw_ui(stdscr, tickers_win, news_win, output_win, cmd_win)
    
    add_message(output_win, "Welcome, Tech Bro. Type 'HELP' to begin!", 4)

    command_buffer = ""
    last_update = time.time()
    
    all_headlines = NEWS_HEADLINES 
    random.shuffle(all_headlines)
    news_scroll_pos = 0
    
    game = BalloonGame()

    while True:
        # Get user input
        try:
            key = stdscr.getch()
        except:
            key = -1
        
        # Process input
        if key != -1:
            if game.active and not game.burst and not game.redeemed:
                # Balloon game controls
                if key == ord(' '):  # SPACE to pump
                    if game.pumps < 30:
                        game.pumps += 1
                        game.current_earnings += 0.20
                        
                        # Check if balloon bursts
                        if game.pumps >= game.max_pumps:
                            game.burst = True
                            game.current_earnings = 0
                            game.rounds_played += 1
                            add_message(output_win, f"BURST at {game.pumps} pumps! Lost everything!", 2)
                            time.sleep(1.5)
                            game.reset_round()
                            game.active = False
                            add_message(output_win, f"Total earnings: £{game.total_earnings:.2f}. Type BALLOON to play again!", 4)
                    else:
                        add_message(output_win, "Maximum pumps reached! Redeem now!", 3)
                
                elif key == ord('r') or key == ord('R'):  # R to redeem
                    if game.pumps > 0:
                        game.redeemed = True
                        game.total_earnings += game.current_earnings
                        game.rounds_played += 1
                        add_message(output_win, f"REDEEMED £{game.current_earnings:.2f}! Total: £{game.total_earnings:.2f}", 1)
                        time.sleep(1.5)
                        game.reset_round()
                        game.active = False
                        add_message(output_win, "Type BALLOON to play again!", 4)
            
            # Command input
            if key == curses.KEY_ENTER or key in [10, 13]:
                if command_buffer and not game.active:
                    action = process_command(command_buffer, output_win, game)
                    if action == "clear":
                        global message_log
                        message_log = []
                        add_message(output_win, "Console cleared.", 4)
                    command_buffer = ""
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                if not game.active:
                    command_buffer = command_buffer[:-1]
            elif 32 <= key <= 126:
                if not game.active:
                    command_buffer += chr(key)
        
        # Update UI periodically
        if time.time() - last_update > 0.2:
            update_tickers(tickers_win)
            news_scroll_pos = scroll_news(news_win, all_headlines, news_scroll_pos)
            last_update = time.time()

        # Draw balloon game if active
        if game.active:
            draw_balloon(output_win, game)
            output_win.box()
            output_win.addstr(0, 2, " BALLOON GAME ", curses.color_pair(3))
            output_win.refresh()
        
        # Redraw command input line
        cmd_win.erase()
        cmd_win.box()
        cmd_win.addstr(0, 2, " COMMAND ", curses.color_pair(3))
        if game.active:
            cmd_win.addstr(1, 2, "> [GAME IN PROGRESS]", curses.color_pair(3))
        else:
            cmd_win.addstr(1, 2, f"> {command_buffer}")
        cmd_win.refresh()

        # Place cursor correctly
        if not game.active:
            stdscr.move(h - 6, 31 + 4 + len(command_buffer))
        stdscr.refresh()
        
        time.sleep(0.01) # Prevents high CPU usage

if __name__ == "__main__":
    # A note for Windows users
    try:
        wrapper(main)
    except curses.error as e:
        print("--- Curses Error ---")
        print("This game requires the 'curses' library.")
        print("On Windows, you may need to install 'windows-curses' first.")
        print("Try running: pip install windows-curses")
        print(f"Error details: {e}")
    except KeyboardInterrupt:
        print("\nExiting Terminal. The markets never sleep.")