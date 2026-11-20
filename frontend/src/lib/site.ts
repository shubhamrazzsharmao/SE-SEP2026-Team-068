export const site = {
  name: "Mosaiq",
  tagline: "One source. Many stories.",
  nav: [
    { label: "How it works", href: "#how-it-works" },
    { label: "Features", href: "#features" },
    { label: "Who it's for", href: "#audience" },
    { label: "FAQ", href: "#faq" },
  ],
  loginHref: "/login",
  ctaHref: "/signup",
  ctaLabel: "Start creating",
  hero: {
    eyebrow: "AI campaign planning for agencies",
    headline: ["One source.", "A whole campaign.", "Approved."],
    sub: "Drop in a blog, report or transcript. Mosaiq plans the campaign, writes every post in your client's voice, and keeps every approval on record.",
    secondaryLabel: "See how it works",
    secondaryHref: "#how-it-works",
    points: [
      { title: "1 source, 12+ posts", text: "Plan and generate platform-ready posts from one document." },
      { title: "Claims checked", text: "Every claim is compared against your source before review." },
      { title: "Approved by version", text: "Edit an approved post and it goes straight back to review." },
    ],
  },
      platforms: [
    { name: "LinkedIn", tag: "MVP", icon: "linkedin" },
    { name: "Instagram", tag: "MVP", icon: "instagram" },
    { name: "Blog", tag: "MVP", icon: "blog" },
    { name: "Facebook", tag: "Soon", icon: "facebook" },
    { name: "X", tag: "Soon", icon: "x" },
    { name: "Threads", tag: "Soon", icon: "threads" },
    { name: "Newsletter", tag: "Soon", icon: "newsletter" },
  ],
  steps: [
    {
      title: "Add your source",
      text: "Upload a blog, report, transcript or brief. Mosaiq extracts the facts, audiences and angles, each linked back to the exact passage.",
    },
    {
      title: "Approve the plan",
      text: "Get a posting calendar with themes, key messages and a CTA for every post. Edit it, then lock it in as your blueprint.",
    },
    {
      title: "Generate posts one by one",
      text: "Each post is drafted for its platform in your client's voice, then fact-checked against your source.",
    },
    {
      title: "Review and approve",
      text: "Clients get a link, with no account needed. Comments, versions and sign-offs are saved, and approval is tied to one exact version.",
    },
  ],
    features: {
    eyebrow: "Features",
    title: "Built for the part after the draft.",
    items: {
      source: { title: "Every claim traced to your source", text: "Hover a sentence to see the passage it came from. Unsupported claims get flagged before anyone reviews." },
      voice: { title: "Brand voice score", text: "Each post is scored against your client's guidelines and samples, with a short reason." },
      client: { title: "Client review, no signup", text: "Clients open a secure link, comment on the exact text, and approve or request changes." },
      versions: { title: "Nothing is overwritten", text: "Every edit and regeneration is a new version, so approvals stay auditable." },
      ideas: { title: "Ideas inbox", text: "Capture a raw idea or link, then turn it into a campaign in one click." },
    },
  },
    audience: {
    eyebrow: "Who it's for",
    title: "One workspace. Everyone who touches the content.",
    items: [
      {
        role: "Freelancers",
        line: "Many clients, one brain.",
        points: ["A separate workspace and brand profile per client", "Turn one source into a month of posts", "Send clients a link, not a PDF"],
        bg: "bg-brand text-white",
      },
      {
        role: "Agencies",
        line: "Clarity for clients, not chaos.",
        points: ["Creators, internal reviewers and owners with clear roles", "Every version and decision on record", "Progress at a glance: 7 of 12 approved"],
        bg: "bg-brown text-paper",
      },
      {
        role: "Clients",
        line: "Approve in minutes.",
        points: ["Open a secure link, with no account or password", "Comment on the exact words you mean", "See only your own content"],
        bg: "bg-white text-ink",
      },
    ],
  },
    faq: {
    eyebrow: "FAQ",
    title: "Questions, answered.",
    items: [
      { q: "What can I upload as a source?", a: "A blog post, article, report, transcript or campaign brief. Mosaiq cleans it, extracts the key facts, audiences and angles, and links each fact back to the passage it came from." },
      { q: "Which platforms does it write for?", a: "LinkedIn, Instagram and blog posts at launch. Each platform has its own rules for length, hashtags and structure, so more platforms can be added without changing the workflow." },
      { q: "Does Mosaiq publish posts for me?", a: "Not yet. Approved posts are exported or copied, and publishing integrations come after launch. Only content approved at its current version can leave the workspace." },
      { q: "How does it keep a client's brand voice?", a: "Each client has a brand profile (tone, audience, rules, product facts) and sample posts. Every draft is generated from them and scored for voice, so output stays on brand." },
      { q: "How do you stop the AI from making things up?", a: "A separate verification pass checks every claim in a draft against your source and flags anything it can't find, before a reviewer ever sees it." },
      { q: "Do clients need an account to approve?", a: "No. Clients get a secure, expiring link that only opens the items assigned to them. They can comment on exact text, approve, or request changes." },
      { q: "What happens if I edit a post after it's approved?", a: "It goes straight back to review. Approval is tied to one specific version, so nothing changes silently after sign-off." },
    ],
  },
};