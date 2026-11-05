import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://voicesphere-ai.vercel.app"),
  title: "VoiceSphere AI - Real-Time Speech Assistant with Live Captions",
  description:
    "A high-performance real-time AI voice assistant powered by Groq Whisper Large v3 and Llama 3.3. Features live speech subtitles, audio waveform visualizer, and streaming multi-language TTS.",
  openGraph: {
    title: "VoiceSphere AI - Real-Time Speech Assistant with Live Captions",
    description:
      "A high-performance real-time AI voice assistant powered by Groq Whisper Large v3 and Llama 3.3. Features live speech subtitles, audio waveform visualizer, and streaming multi-language TTS.",
    url: "https://voicesphere-ai.vercel.app",
    siteName: "VoiceSphere AI",
    images: [
      {
        url: "/og-image.png?v=2",
        width: 1200,
        height: 630,
        alt: "VoiceSphere AI - Real-Time Speech Assistant Preview",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "VoiceSphere AI - Real-Time Speech Assistant with Live Captions",
    description:
      "A high-performance real-time AI voice assistant powered by Groq Whisper Large v3 and Llama 3.3. Features live speech subtitles, audio waveform visualizer, and streaming multi-language TTS.",
    images: ["/og-image.png?v=2"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
