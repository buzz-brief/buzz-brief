<p align="center">
  <a href="https://www.youtube.com/shorts/oFaW2A6t9D0" title="Watch the demo on YouTube">
    <img src="https://img.youtube.com/vi/oFaW2A6t9D0/maxresdefault.jpg" alt="BuzzBrief — demo" width="720">
  </a>
</p>
<p align="center">
  <a href="https://www.youtube.com/shorts/oFaW2A6t9D0" title="Watch the demo on YouTube">
    <img src="https://img.shields.io/badge/Watch%20the%20demo-YouTube-red?logo=youtube&logoColor=white" alt="Watch the demo on YouTube">
  </a>
</p>



## Inspiration
Do you ever get bored scrolling through hundreds of emails, having to read each one separately? It’s not only time-consuming but also mentally draining. That’s when we thought, what if you could digest all your emails easily and actually enjoy it? Imagine consuming your inbox not by reading walls of text, but by watching short, fun, TikTok-style clips that summarize everything for you. Turn a daily hassle into an engaging, exciting, and captivating experience. That’s exactly what inspired Buzz Brief, to transform boring inboxes into entertaining daily briefings.

## What it does
Buzz Brief is a mobile application that transforms your daily inbox into a fun, scrollable video feed. It provides:

1. **Email Extraction**
 - Seamlessly connects to your Gmail account using Google’s secure OAuth flow.
 - Automatically retrieves your latest emails each day without any manual setup.
 - Parses and structures email content to prepare it for summarization.

2. **AI Summarization & Script Generation**
 - Uses large language models to summarize each email into short, engaging scripts.
 - Adds a humorous and lighthearted tone to make the content fun to consume.
 - Employs agenetic AI workflows to generate context-aware scripts for each message.

3. **Audio & Video Creation**
 - Converts generated scripts into natural-sounding speech using text-to-speech models.
 - Pairs the narration with dynamic background videos, music, and auto-generated subtitles.
 - Produces short, TikTok-style video clips for each email, optimized for quick viewing.

4. **Interactive Video Feed**
 - Displays all generated clips in a vertically scrollable interface inspired by TikTok and Instagram Reels.
 - Allows users to pause, mute, or swipe through their “email videos” just like social media.
 - Preloads clips and caches them locally to ensure smooth playback and minimal delays.
 - Enables users to directly from the video feed for later review, adding a quick way to save key content without leaving the app.

All processing is handled through a secure Gmail API connection combined with efficient AI pipelines, enabling users to stay informed in a way that’s fast, engaging, and entertaining.

## How we built it

1. **Technology Stack:**
**Frontend**:
- Built with React Native and Expo Go for rapid mobile development and testing across platforms.
- Implemented a TikTok-style video feed with smooth scrolling, pause/mute controls, and flagging functionality.
- Leveraged React Native’s video player libraries and custom hooks for efficient state management and caching.

**Backend:**
- Developed using FastAPI (Python) to handle email retrieval, LLM processing, and media generation.
- Integrated the Gmail API for secure daily email extraction using OAuth 2.0.
- Used OpenAI GPT-3.5 Turbo to generate short, humorous scripts summarizing each email.
- Used OpenAI TTS-1 for text-to-speech conversion to produce natural-sounding voiceovers.
- Employed FFmpeg for stitching together audio, background videos, and subtitles into final TikTok-style clips.
- Integrated Supabase to serve as the centralized backend database for storing both raw email content and generated video metadata.

## Challenges we ran into
1. **Gmail API Integration:**
- Authenticating securely with Google’s OAuth flow and handling various email formats (HTML, plaintext, threaded conversations) required careful parsing logic and multiple rounds of testing.

2. **LLM Pipeline Efficiency:**
- Designing a multi-step agentic workflow including summarization, script generation, text-to-speech, and video rendering while keeping processing times short was tricky. We had to balance speed, cost, and output quality through prompt tuning and pipeline optimization.

3. **Video Generation Latency:**
Combining audio, subtitles, and background video clips using FFmpeg introduced timing challenges. We iteratively optimized encoding parameters and parallelized tasks to reduce rendering delays.

4. **UI Responsiveness:**
Building a TikTok-style video feed that feels smooth required fine-tuning preloading, caching, and state management in React Native. Ensuring videos play seamlessly while allowing flagging, muting, and pausing took significant iteration.

5. **Cross-Component Integration:**
Merging the frontend UI, email extraction backend, and LLM media pipeline into a single, cohesive app surfaced bugs related to timing, data formatting, and async behavior. Coordinating these parts under tight time constraints was challenging but a very rewarding experience.

## Accomplishments that we're proud of
1. **End-to-End Working Prototype:**
- Built a nearly fully functional mobile app in just 36 hours that connects to Gmail, processes emails using LLMs, and generates TikTok-style video summaries, with all elements integrated seamlessly.

2. **Innovative Email Consumption Experience:**
Transformed the traditionally tedious act of reading emails into a fun, scrollable video feed with engaging scripts, natural-sounding narration, and smooth UI interactions.

3. **Fast & Efficient Media Pipeline:**
Successfully combined OpenAI’s GPT-3.5-Turbo, TTS-1, and FFmpeg into a streamlined backend pipeline that can summarize, generate speech, and produce videos quickly with minimal lag.

4. **Strong Team Learning Curve:**
None of us started with deep experience in Gmail APIs, agentic AI pipelines, or automated video generation. We rapidly picked up these tools and techniques to deliver a polished result under hackathon time pressure.

5. **Robust Modular Architecture:**
Structured the system into clear layers including email extraction, AI summarization, media generation, and UI. This made parallel development, debugging, and integration far smoother.

## What we learned
What we learned
1. **Building Agentic LLM Pipelines:**
- We gained hands-on experience designing multi-step AI workflows  from summarization to script generation to TTS and learned how to optimize them for speed, cost, and output quality.

2. **TikTok-Style UX Design:**
- Studying popular short-form content platforms taught us how crucial preloading, smooth scrolling, and intuitive interactions are for user engagement. A slick UX can make or break the product.

3. **Email API Integration:**
- Working with the Gmail API gave us a deep understanding of secure OAuth flows, message parsing, and handling different email formats which are skills that will transfer to other integrations like Outlook or custom inboxes.

4. **Multimedia Generation Techniques:**
- We learned how to combine text, speech, video, and subtitles using tools like FFmpeg to create polished, short-form videos dynamically and efficiently.

5. **Team Coordination Under Pressure:**
- With multiple components (frontend, backend, AI pipeline) in parallel, we developed better strategies for modular development, clear interfaces, and quick debugging, which proved essential in a 36-hour hackathon setting.

## What's next for Buzz Brief
1. **Expanded Email Provider Support:**
- Extend beyond Gmail to include Outlook, Yahoo, and other major email services, allowing users to centralize their inboxes in one engaging feed.

2. **Multi-Account Integration:**
- Enable users to connect and manage multiple email accounts simultaneously, making Buzz Brief a true all-in-one daily briefing hub.

3. **Custom Content Sources:**
- Allow users to add newsletters, websites, or even social media feeds (like Twitter/X) as additional content streams, turning the app into a personalized infotainment dashboard.

4. **Smarter Personalization:**
- Incorporate user preferences and interaction patterns to tailor tone, video style, and prioritization — ensuring the most relevant and entertaining content is surfaced first.

5. **UI & Performance Optimization:**
- Further refine the TikTok-style UI for faster loading, smoother transitions, and improved caching, while reducing media generation latency for near real-time updates.
