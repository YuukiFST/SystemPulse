import customtkinter as ctk
import threading
import socket
import struct
import select
import random
from datetime import datetime
from gui.base_dialog import ScrollableDialog
from gui.theme import (
    BG_CARD, BG_ELEVATED, BORDER_SUBTLE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_EMERALD,
    ACCENT_PINK, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, TEXT_SUCCESS, TEXT_WARNING,
    TEXT_ERROR, GlowButton, create_section_label
)
from utils.constants import PING_TARGET_SAMPLES, PING_TIMEOUT_SEC


GAMING_SERVERS = {
    "NA-East": "ping-nae.ds.on.epicgames.com",
    "NA-Central": "ping-nac.ds.on.epicgames.com",
    "NA-West": "ping-naw.ds.on.epicgames.com",
    "Europe": "ping-eu.ds.on.epicgames.com",
    "Oceania": "ping-oce.ds.on.epicgames.com",
    "Brazil": "ping-br.ds.on.epicgames.com",
    "Asia": "ping-asia.ds.on.epicgames.com",
    "Cloudflare (Global)": "1.1.1.1",
    "Google DNS": "8.8.8.8",
}


def checksum(source_string):
    sum_val = 0
    max_count = (len(source_string) // 2) * 2
    count = 0
    while count < max_count:
        val = source_string[count + 1] * 256 + source_string[count]
        sum_val = sum_val + val
        sum_val = sum_val & 0xffffffff
        count = count + 2

    if max_count < len(source_string):
        sum_val = sum_val + source_string[len(source_string) - 1]
        sum_val = sum_val & 0xffffffff

    sum_val = (sum_val >> 16) + (sum_val & 0xffff)
    sum_val = sum_val + (sum_val >> 16)
    answer = ~sum_val
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def create_packet(packet_id, size=59):
    header = struct.pack("bbHHh", 8, 0, 0, packet_id, 1)
    data = size * "Q"
    my_checksum = checksum(header + data.encode('utf-8'))
    header = struct.pack("bbHHh", 8, 0, socket.htons(my_checksum), packet_id, 1)
    return header + data.encode('utf-8')


def ping_host(host):
    try:
        icmp = socket.getprotobyname("icmp")
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        sock.settimeout(PING_TIMEOUT_SEC)
    except (socket.error, OSError, PermissionError):
        return None

    try:
        my_id = datetime.now().microsecond & 0xFFFF
        packet = create_packet(my_id)
        sent_time = datetime.now()
        sock.sendto(packet, (host, 1))

        while True:
            ready = select.select([sock], [], [], PING_TIMEOUT_SEC)
            if ready[0] == []:
                sock.close()
                return None

            time_received = datetime.now()
            rec_packet, addr = sock.recvfrom(1024)
            icmp_header = rec_packet[20:28]
            type_code, code, chksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)
            if packet_id == my_id:
                sock.close()
                return (time_received - sent_time).total_seconds() * 1000
    except (socket.error, OSError, struct.error):
        pass
    finally:
        try:
            sock.close()
        except (socket.error, OSError):
            pass
    return None


def game_simulation(ping_data, num_rounds=10, extra_lag=0):
    player1_wins = 0
    player2_wins = 0
    data_len = len(ping_data)
    
    p1_start = random.randint(0, data_len - 1)
    p2_start = random.randint(0, data_len - 1)
    
    for round_num in range(num_rounds):
        p1_idx = (p1_start + round_num) % data_len
        p2_idx = (p2_start - round_num - 2) % data_len
        
        p1_latency = ping_data[p1_idx]
        p2_latency = ping_data[p2_idx] + extra_lag
        
        if p1_latency < p2_latency:
            player1_wins += 1
        else:
            player2_wins += 1
    
    return player1_wins, player2_wins


def calculate_speed_limit(ping_data, rounds=10, games=100, resolution=0.1, max_lag=30, target_90=0.90, target_80=0.80):
    extra_lag = 0
    
    while extra_lag <= max_lag:
        p1_total = 0
        p2_total = 0
        
        for _ in range(games):
            p1, p2 = game_simulation(ping_data, rounds, extra_lag)
            p1_total += p1
            p2_total += p2
        
        total_games = p1_total + p2_total
        win_rate = p1_total / total_games if total_games > 0 else 0
        
        if win_rate >= target_90:
            return extra_lag, win_rate, True
        
        if win_rate >= target_80:
            return extra_lag, win_rate, False
        
        extra_lag += resolution
    
    return max_lag, 0.5, False


class InputLagDialog(ScrollableDialog):
    def __init__(self, parent):
        self._server_var = None
        self._ping_data = []
        self._running = False
        self._ping_count = 0
        self._target_pings = PING_TARGET_SAMPLES
        self._current_ping = 0
        self._speed_limit = None
        self._win_rate = None
        
        super().__init__(
            parent,
            title="Network Latency Tester",
            header_text="Network Latency Tester",
            geometry="550x500",
            accent_color=ACCENT_PINK
        )
    
    def _build_header_extra(self, header: ctk.CTkFrame) -> None:
        self._status_label = ctk.CTkLabel(
            header, text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED
        )
        self._status_label.pack(side="right")
    
    def _build_content_area(self) -> None:
        super()._build_content_area()
        self._clear_scroll_frame()
        self._build_main_ui()
    
    def _build_main_ui(self) -> None:
        info_card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=12,
            border_color=BORDER_SUBTLE, border_width=1
        )
        info_card.pack(fill="x", padx=16, pady=(12, 8))
        
        inner = ctk.CTkFrame(info_card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        
        ctk.CTkLabel(
            inner, text="How it works",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=13),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            inner,
            text="Measures network latency and simulates competitive gaming\nscenarios to find your input lag 'speed limit'.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))
        
        server_card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=12,
            border_color=BORDER_SUBTLE, border_width=1
        )
        server_card.pack(fill="x", padx=16, pady=8)
        
        server_inner = ctk.CTkFrame(server_card, fg_color="transparent")
        server_inner.pack(fill="x", padx=16, pady=14)
        
        ctk.CTkLabel(
            server_inner, text="Select Server",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        self._server_var = ctk.StringVar(value="Cloudflare (Global)")
        server_menu = ctk.CTkOptionMenu(
            server_inner,
            variable=self._server_var,
            values=list(GAMING_SERVERS.keys()),
            fg_color=BG_ELEVATED,
            button_color=BG_ELEVATED,
            button_hover_color=ACCENT_PINK,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=BG_ELEVATED,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=280,
            command=self._on_server_change
        )
        server_menu.pack(anchor="w", pady=(8, 0))
        
        self._ping_label = ctk.CTkLabel(
            server_inner, text="Current ping: --",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_MUTED
        )
        self._ping_label.pack(anchor="w", pady=(8, 0))
        
        progress_card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=12,
            border_color=BORDER_SUBTLE, border_width=1
        )
        progress_card.pack(fill="x", padx=16, pady=8)
        
        progress_inner = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_inner.pack(fill="x", padx=16, pady=14)
        
        ctk.CTkLabel(
            progress_inner, text="Data Collection",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        self._progress_bar = ctk.CTkProgressBar(
            progress_inner, progress_color=ACCENT_PINK, fg_color=BG_ELEVATED,
            height=8, corner_radius=4
        )
        self._progress_bar.pack(fill="x", pady=(8, 4))
        self._progress_bar.set(0)
        
        self._progress_label = ctk.CTkLabel(
            progress_inner, text=f"0 / {self._target_pings} samples",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED
        )
        self._progress_label.pack(anchor="w")
        
        result_card = ctk.CTkFrame(
            self.scroll_frame, fg_color=BG_CARD, corner_radius=12,
            border_color=ACCENT_PINK, border_width=2
        )
        result_card.pack(fill="x", padx=16, pady=8)
        
        result_inner = ctk.CTkFrame(result_card, fg_color="transparent")
        result_inner.pack(fill="x", padx=16, pady=14)
        
        ctk.CTkLabel(
            result_inner, text="Input Lag Speed Limit",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=13),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        self._result_label = ctk.CTkLabel(
            result_inner, text="--",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=ACCENT_PINK
        )
        self._result_label.pack(anchor="w", pady=(4, 0))
        
        self._result_desc = ctk.CTkLabel(
            result_inner, text="Start the test to calculate your speed limit",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED
        )
        self._result_desc.pack(anchor="w", pady=(2, 0))
        
        btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(12, 8))
        
        self._start_btn = GlowButton(
            btn_frame, text="Start Test", command=self._start_test,
            accent=ACCENT_PINK, width=140
        )
        self._start_btn.pack(side="left")
        
        self._stop_btn = GlowButton(
            btn_frame, text="Stop", command=self._stop_test,
            accent=TEXT_WARNING, width=100
        )
        self._stop_btn.pack(side="left", padx=(10, 0))
        self._stop_btn.configure(state="disabled")
    
    def _build_footer_left(self, footer: ctk.CTkFrame) -> None:
        pass
    
    def _show_loading(self, message: str = "Loading...") -> None:
        pass
    
    def _on_server_change(self, value) -> None:
        self._ping_data.clear()
        self._ping_count = 0
        self._update_progress()
        self._result_label.configure(text="--")
        self._result_desc.configure(text="Server changed - start a new test")
    
    def _start_test(self) -> None:
        self._ping_data.clear()
        self._ping_count = 0
        self._running = True
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._status_label.configure(text="Running...", text_color=ACCENT_PINK)
        self._result_label.configure(text="--")
        self._result_desc.configure(text="Collecting ping data...")
        
        threading.Thread(target=self._collect_pings, daemon=True).start()
    
    def _stop_test(self) -> None:
        self._running = False
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._status_label.configure(text="Stopped", text_color=TEXT_WARNING)
    
    def _collect_pings(self) -> None:
        server_name = self._server_var.get()
        host = GAMING_SERVERS.get(server_name, "1.1.1.1")
        
        try:
            host_ip = socket.gethostbyname(host)
        except socket.gaierror:
            self.after(0, lambda: self._show_error("Could not resolve server address"))
            return
        
        while self._running and self._ping_count < self._target_pings:
            ping_ms = ping_host(host_ip)
            
            if ping_ms is not None:
                self._ping_data.append(ping_ms)
                self._ping_count += 1
                self._current_ping = ping_ms
                self.after(0, self._update_ui)
            
            if not self._running:
                break
        
        if self._running and len(self._ping_data) >= self._target_pings:
            self.after(0, self._calculate_result)
    
    def _update_ui(self) -> None:
        if self._is_destroyed:
            return
        
        self._ping_label.configure(text=f"Current ping: {self._current_ping:.1f} ms")
        self._update_progress()
    
    def _update_progress(self) -> None:
        if self._is_destroyed:
            return
        
        progress = self._ping_count / self._target_pings
        self._progress_bar.set(progress)
        self._progress_label.configure(text=f"{self._ping_count} / {self._target_pings} samples")
    
    def _calculate_result(self) -> None:
        if self._is_destroyed:
            return
        
        self._status_label.configure(text="Calculating...", text_color=ACCENT_CYAN)
        self._result_desc.configure(text="Running game simulations...")
        
        threading.Thread(target=self._run_calculation, daemon=True).start()
    
    def _run_calculation(self) -> None:
        speed_limit, win_rate, is_90 = calculate_speed_limit(self._ping_data)
        self.after(0, lambda: self._show_result(speed_limit, win_rate, is_90))
    
    def _show_result(self, speed_limit, win_rate, is_90) -> None:
        if self._is_destroyed:
            return
        
        self._running = False
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        
        rate_pct = int(win_rate * 100)
        
        if is_90:
            self._result_label.configure(text=f"{speed_limit:.1f} ms @ 90%", text_color=ACCENT_EMERALD)
            desc = f"Minimum lag to gain 90% win rate advantage"
            self._status_label.configure(text="Complete", text_color=TEXT_SUCCESS)
        elif win_rate >= 0.80:
            self._result_label.configure(text=f"{speed_limit:.1f} ms @ {rate_pct}%", text_color=ACCENT_CYAN)
            desc = f"Minimum lag to gain {rate_pct}% win rate advantage"
            self._status_label.configure(text="Complete", text_color=TEXT_SUCCESS)
        else:
            self._result_label.configure(text="< 0.1 ms", text_color=TEXT_SUCCESS)
            desc = "Your connection is very consistent!"
            self._status_label.configure(text="Complete", text_color=TEXT_SUCCESS)
        
        avg_ping = sum(self._ping_data) / len(self._ping_data)
        min_ping = min(self._ping_data)
        max_ping = max(self._ping_data)
        jitter = max_ping - min_ping
        
        self._result_desc.configure(
            text=f"{desc}\nAvg: {avg_ping:.1f}ms | Jitter: {jitter:.1f}ms | Range: {min_ping:.1f}-{max_ping:.1f}ms"
        )
    
    def _show_error(self, msg) -> None:
        if self._is_destroyed:
            return
        
        self._running = False
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._status_label.configure(text="Error", text_color=TEXT_ERROR)
        self._result_desc.configure(text=f"Error: {msg}")
    
    def _can_close(self) -> bool:
        self._running = False
        return True


def show_input_lag_dialog(parent) -> None:
    dialog = InputLagDialog(parent)
    dialog.wait_window()
