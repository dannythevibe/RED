using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using Newtonsoft.Json.Linq;

namespace DynamicWin.Utils
{
    public static class RedBridgeClient
    {
        private const string Host = "127.0.0.1";
        private const int Port = 8282;

        private static TcpClient _client;
        private static StreamWriter _writer;
        private static bool _isRunning = false;

        public static string CurrentMode { get; private set; } = "idle";
        public static string LastReply { get; private set; } = "";

        public static event Action<string> OnModeChanged;
        public static event Action<string> OnReplyReceived;

        public static void Start()
        {
            if (_isRunning) return;
            _isRunning = true;

            Task.Run(ConnectionLoop);
        }

        private static async Task ConnectionLoop()
        {
            while (_isRunning)
            {
                try
                {
                    _client = new TcpClient();
                    await _client.ConnectAsync(Host, Port);
                    
                    var stream = _client.GetStream();
                    _writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true };
                    var reader = new StreamReader(stream, Encoding.UTF8);

                    System.Diagnostics.Debug.WriteLine("🚩 RedBridgeClient: Connected to RED Core on 127.0.0.1:8282");

                    while (_client.Connected && _isRunning)
                    {
                        string line = await reader.ReadLineAsync();
                        if (line == null) break;

                        ProcessMessage(line);
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"🚩 RedBridgeClient: Connection error or offline ({ex.Message}). Retrying in 3s...");
                }
                finally
                {
                    _writer = null;
                    _client?.Close();
                }

                await Task.Delay(3000);
            }
        }

        private static void ProcessMessage(string rawJson)
        {
            try
            {
                var json = JObject.Parse(rawJson);
                string action = json.Value<string>("action");

                if (action == "set_mode")
                {
                    string mode = json.Value<string>("mode") ?? "idle";
                    CurrentMode = mode;
                    Application.Current.Dispatcher.Invoke(() => OnModeChanged?.Invoke(mode));
                }
                else if (action == "show_reply")
                {
                    string text = json.Value<string>("text") ?? "";
                    LastReply = text;
                    Application.Current.Dispatcher.Invoke(() => OnReplyReceived?.Invoke(text));
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"🚩 RedBridgeClient: JSON decode error: {ex.Message}");
            }
        }

        public static void SendUserInput(string text)
        {
            if (_writer == null) return;
            try
            {
                var payload = new JObject
                {
                    ["action"] = "user_input",
                    ["text"] = text
                }.ToString(Newtonsoft.Json.Formatting.None) + "\n";

                _writer.Write(payload);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"🚩 RedBridgeClient: Send error: {ex.Message}");
            }
        }
    }
}
