import type { IconType } from "react-icons";
import { FaLinkedinIn, FaInstagram, FaFacebookF, FaXTwitter } from "react-icons/fa6";
import { SiThreads } from "react-icons/si";
import { LuPenLine, LuMail } from "react-icons/lu";
import { site } from "@/lib/site";

const icons: Record<string, IconType> = {
  linkedin: FaLinkedinIn,
  instagram: FaInstagram,
  facebook: FaFacebookF,
  x: FaXTwitter,
  threads: SiThreads,
  blog: LuPenLine,
  newsletter: LuMail,
};

export function PlatformStrip() {
  const base = site.platforms;
  const items = [...base, ...base];

  return (
    <section className="border-y border-line bg-paper py-8">
      <p className="text-center text-sm font-medium text-muted">
        Writes natively for every platform your clients are on
      </p>
      <div className="mt-5 overflow-hidden [mask-image:linear-gradient(to_right,transparent,#000_10%,#000_90%,transparent)]">
        <ul className="marquee flex w-max">
          {items.map((p, i) => {
            const Icon = icons[p.icon];
            return (
              <li
                key={`${p.name}-${i}`}
                aria-hidden={i >= base.length}
                className="mr-3 flex items-center gap-3 rounded-full border border-line bg-white py-2 pl-2 pr-4"
              >
                <span className="grid h-8 w-8 place-items-center rounded-full bg-ink text-paper">
                  {Icon && <Icon size={15} />}
                </span>
                <span className="text-sm font-semibold">{p.name}</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    p.tag === "MVP" ? "bg-green-100 text-green-700" : "bg-line text-muted"
                  }`}
                >
                  {p.tag}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}