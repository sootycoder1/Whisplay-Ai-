# ============================================================
# WHISPLAY DISPLAY UI — STAGE 4200
# Chat Runtime Display System
# ============================================================

import sys

sys.path.append(
    "/home/pi/Whisplay/Driver"
)

from WhisPlay import WhisPlayBoard

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)


# ============================================================
# RGB888 → RGB565
# ============================================================

def rgb888_to_rgb565(img):

    data = bytearray()

    for r, g, b in img.getdata():

        rgb565 = (
            ((r & 0xF8) << 8)
            |
            ((g & 0xFC) << 3)
            |
            (b >> 3)
        )

        data.append(rgb565 >> 8)

        data.append(rgb565 & 0xFF)

    return data


# ============================================================
# DISPLAY UI
# ============================================================

class WhisplayUI:


    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.board = WhisPlayBoard()

        self.board.set_backlight(90)

        self.width = self.board.LCD_WIDTH

        self.height = self.board.LCD_HEIGHT


        # ----------------------------------------------------
        # FONTS
        # ----------------------------------------------------

        self.font_small = ImageFont.truetype(

            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSans.ttf",

              20
        )

        self.font_status = ImageFont.truetype(

            "/usr/share/fonts/truetype/dejavu/"
            "DejaVuSans-Bold.ttf",

              22
        )


        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.chat_lines = []

        self.state = "idle"

        self._last_frame = None


        # ----------------------------------------------------
        # INITIAL RENDER
        # ----------------------------------------------------

        self._render()


    # ========================================================
    # UPDATE UI
    # ========================================================

    def update(

        self,

        state=None,

        user=None,

        assistant=None,
    ):

        if state:

            self.state = state


        if user:

            self.chat_lines.append(
                f"You: {user}"
            )


        if assistant:

            self.chat_lines.append(
                f"AI: {assistant}"
            )


        # ----------------------------------------------------
        # LIMIT HISTORY
        # ----------------------------------------------------

        self.chat_lines = (
            self.chat_lines[-10:]
        )


        self._render()


    # ========================================================
    # TEXT WRAP
    # ========================================================

    def _wrap(self, text):

        words = text.split()

        lines = []

        current = ""


        for word in words:

            test = current + (
                " " if current else ""
            ) + word


            if (

                self.font_small.getlength(test)

                < (self.width - 40)

            ):

                current = test

            else:

                lines.append(current)

                current = word


        if current:

            lines.append(current)


        return lines


    # ========================================================
    # RENDER
    # ========================================================

    def _render(self):

        frame_sig = (

            tuple(self.chat_lines),

            self.state,
        )


        # ----------------------------------------------------
        # SKIP DUPLICATE FRAME
        # ----------------------------------------------------

        if frame_sig == self._last_frame:
            return


        self._last_frame = frame_sig


        # ----------------------------------------------------
        # BASE IMAGE
        # ----------------------------------------------------

        img = Image.new(

            "RGB",

            (self.width, self.height),

            (12, 12, 16)
        )

        draw = ImageDraw.Draw(img)


        # ====================================================
        # STATUS BAR
        # ====================================================

        status_colors = {

            "idle":
                (0, 200, 255),

            "listening":
                (0, 255, 120),

            "thinking":
                (255, 180, 0),

            "speaking":
                (255, 90, 90),

            "error":
                (255, 0, 0),

            "loading":
                (150, 150, 255),
        }


        status_text = self.state.upper()

        status_color = status_colors.get(

            self.state,

            (0, 200, 255)
        )


        draw.rectangle(

            (0, 0, self.width, 44),

            fill=(25, 25, 35)
        )


        draw.text(

            (14, 12),

            status_text,

            fill=status_color,

            font=self.font_status
        )


        draw.line(

            (0, 44, self.width, 44),

            fill=(60, 60, 75)
        )


        # ====================================================
        # CHAT AREA
        # ====================================================

        chat_top = 55

        chat_bottom = self.height - 12

        available_height = (
            chat_bottom - chat_top
        )


        wrapped_lines = []


        for line in self.chat_lines:

            wrapped_lines.extend(
                self._wrap(line)
            )


        line_height = 28

        max_visible = (
            available_height // line_height
        )


        visible_lines = wrapped_lines[
            -max_visible:
        ]


        y = chat_top


        for line in visible_lines:


            # ------------------------------------------------
            # USER MESSAGE
            # ------------------------------------------------

            if line.startswith("You:"):

                bubble_color = (
                    40,
                    80,
                    140
                )

                text_color = (
                    255,
                    255,
                    255
                )

                x_offset = 20


            # ------------------------------------------------
            # AI MESSAGE
            # ------------------------------------------------

            else:

                bubble_color = (
                    65,
                    65,
                    75
                )

                text_color = (
                    230,
                    230,
                    230
                )

                x_offset = 10


            text_width = (
                self.font_small.getlength(line)
            )


            bubble_width = text_width + 24


            draw.rounded_rectangle(

                (
                    x_offset - 10,
                    y - 6,

                    x_offset + bubble_width,
                    y + 22,
                ),

                radius=10,

                fill=bubble_color
            )


            draw.text(

                (x_offset, y),

                line,

                fill=text_color,

                font=self.font_small
            )


            y += line_height


        # ====================================================
        # FINAL OUTPUT
        # ====================================================

        img = img.convert("RGB")

        image_data = rgb888_to_rgb565(img)


        self.board.draw_image(

            0,
            0,

            self.width,
            self.height,

            image_data
        )

# ============================================================
# STAGE 4300 RUNTIME-SAFE WRAPPER
# Keeps original Stage 4200 WhisplayUI intact, then extends it.
# ============================================================

_BaseWhisplayUI = WhisplayUI


class WhisplayUI(_BaseWhisplayUI):

    def show_idle(self, message="Idle"):
        return self.update(state="idle", assistant=str(message))

    def show_listening(self, message="Listening"):
        return self.update(state="listening", assistant=str(message))

    def show_thinking(self, message="Thinking"):
        return self.update(state="thinking", assistant=str(message))

    def show_speaking(self, message="Speaking"):
        return self.update(state="speaking", assistant=str(message))

    def show_error(self, message="Error"):
        return self.update(state="error", assistant=str(message))

    def show_message(self, user=None, assistant=None, state=None):
        return self.update(state=state, user=user, assistant=assistant)
