import { Navbar } from "@/components/landing/navbar";
import { Hero } from "@/components/landing/hero";
import { PlatformStrip } from "@/components/landing/platform-strip";
import { HowItWorks } from "@/components/landing/how-it-works";
import { Features } from "@/components/landing/features";
import { Audience } from "@/components/landing/audience";
import { Faq } from "@/components/landing/faq";


export default function Home() {
  return (
    <main>
      <Navbar />
      <Hero />
      <PlatformStrip />
      <HowItWorks />
      <Features />
      <Audience />
      <Faq />
    </main>
  );
}