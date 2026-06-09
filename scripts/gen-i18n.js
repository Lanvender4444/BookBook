// gen-i18n.js — ESM script to generate 61 language translation files
// Usage: node scripts/gen-i18n.js

import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outputDir = join(__dirname, '..', 'frontend', 'src', 'i18n');

const en = {
  nav: { generate: "Generate", history: "History", library: "Library", network: "Network" },
  generate: {
    title: "Generate eBook", description: "Describe the book you want to generate",
    placeholder: "e.g., An introductory book about artificial intelligence for beginners...",
    difficulty: "Difficulty", wordCount: "Target Word Count", chapterCount: "Chapter Count",
    style: "Style", language: "Output Language", start: "Start Generating", generating: "Generating...",
    cancel: "Cancel", outlinePreview: "Outline Preview", progress: "Generation Progress",
    taskRunning: "Task #{id} · Switching pages won't interrupt generation",
    completed: "Generation completed!", reconnecting: "Reconnecting...", reconnectFailed: "Reconnection failed",
    cancelled: "Cancelled", error: "Error", preparing: "Preparing...", simple: "Easy", medium: "Medium", hard: "Hard"
  },
  history: {
    title: "Generation History", newGenerate: "New Generation", all: "All", pending: "In Progress",
    completed: "Completed", failed: "Failed", deleted: "Deleted", noRecords: "No history records",
    goGenerate: "Generate an eBook", viewProgress: "View Progress", cancel: "Cancel",
    read: "Read", regenerate: "Regenerate", delete: "Delete", createdAt: "Created",
    completedAt: "Completed", difficulty: "Difficulty", wordCount: "Target Words", chapters: "chapters",
    realtimeProgress: "Real-time Progress", processing: "Processing...",
    chapter: "Chapter {current}", totalChapters: "Total {total} chapters", outline: "Outline", error: "Error",
    confirmDelete: "Are you sure you want to delete this record? This action cannot be undone.",
    confirmDeleteTitle: "Delete Record"
  },
  library: {
    title: "My Library", settings: "Settings", userInfo: "User Info", userId: "User ID",
    booksDir: "Book Save Location", save: "Save", currentDir: "Current Location",
    all: "All", local: "Local", p2p: "P2P Source", noBooks: "No books yet, generate one!",
    read: "Read", delete: "Delete", chapters: "{count} chapters",
    confirmDelete: "Are you sure you want to delete this book? Local files will also be deleted. This action cannot be undone.",
    confirmDeleteTitle: "Delete Book", saved: "Save location updated"
  },
  network: {
    title: "P2P Network", myInfo: "My Node Info", userId: "User ID", ip: "IP Address",
    bookCount: "Book Count", nodes: "Online Nodes", noNodes: "No other online nodes",
    books: "Shared Books", noBooks: "No shared books", download: "Download", downloading: "Downloading...",
    downloadSuccess: "Book downloaded successfully!", downloadFailed: "Download failed",
    confirmDownload: "Do you want to download this book?", local: "Local", p2p: "P2P",
    shareTab: "Share", connectTab: "Connect", redeemTab: "Receive",
    createShare: "Create Share Link", selectBook: "Select Book", allBooks: "All Books",
    expireTime: "Expiration", hour: "hour", hours: "hours", days: "days",
    generateLink: "Generate Link", myShareLinks: "My Share Links", noShareLinks: "No share links yet",
    copy: "Copy", expiresAt: "Expires at", connectPeer: "Connect to Peer",
    peerAddress: "Peer Address", peerPort: "Port", connecting: "Connecting...",
    connect: "Connect", connected: "Connected", connectFailed: "Connection failed",
    peerBooks: "Peer Books", redeemShare: "Receive via Share Link",
    redeemHelpDesc: "Paste the share link or token to receive books", shareToken: "Share Token",
    peerHost: "Peer Host", redeemBtn: "Receive Book", redeemFailed: "Receive failed",
    shareCreated: "Share link created", shareHelpTitle: "How to Use Share Links",
    shareHelpDesc: "Send the generated link to your peer. They can paste it in the 'Receive' tab to get your books."
  },
  reader: { loading: "Loading...", notFound: "Book not found", back: "Back to Library" },
  modal: { confirm: "Confirm", cancel: "Cancel" }
};

const translations = {};

// af — Afrikaans
translations.af = {
  nav: { generate: "Genereer", history: "Geskiedenis", library: "Bibliotheek", network: "Netwerk" },
  generate: { title: "Genereer eBoek", description: "Beskryf die boek wat jy wil genereer", placeholder: "bv. 'n Inleidende boek oor kunsmatige intelligensie vir beginners...", difficulty: "Moeilikheid", wordCount: "Teikenaantal woorde", chapterCount: "Aantal hoofstukke", style: "Styl", language: "AfvoerTaal", start: "Begin Genereer", generating: "Genereer...", cancel: "Kanselleer", outlinePreview: "Skets Voorskou", progress: "GenereerVordering", taskRunning: "Taak #{id} · Bladsyverandering onderbreek nie genereer nie", completed: "Genereering voltooid!", reconnecting: "Herkoppel...", reconnectFailed: "Herkoppeling misluk", cancelled: "Gekanselleer", error: "Fout", preparing: "Voorberei...", simple: "Maklik", medium: "Medium", hard: "Moeilik" },
  history: { title: "GenereerGeskiedenis", newGenerate: "Nuwe Genereer", all: "Alles", pending: "Aan die Gang", completed: "Voltooid", failed: "Misluk", deleted: "Verwyder", noRecords: "Geen geskiedenis rekords nie", goGenerate: "Genereer 'n eBoek", viewProgress: "Sien Vordering", cancel: "Kanselleer", read: "Lees", regenerate: "HerGenereer", delete: "Verwyder", createdAt: "Geskep", completedAt: "Voltooid", difficulty: "Moeilikheid", wordCount: "Teikenwoorde", chapters: "hoofstukke", realtimeProgress: "VerblyfVordering", processing: "Verwerk...", chapter: "Hoofstuk {current}", totalChapters: "Totaal {total} hoofstukke", outline: "Skets", error: "Fout", confirmDelete: "Is jy seker jy wil hierdie rekord skrap? Hierdie aksie kan nie ongedaan gemaak word nie.", confirmDeleteTitle: "Skrap Rekord" },
  library: { title: "My Bibliotheek", settings: "Instellings", userInfo: "GebruikerInfo", userId: "GebruikerID", booksDir: "Boek Bergingsplek", save: "Berg", currentDir: "Huidige Plek", all: "Alles", local: "Lokaal", p2p: "P2P Bron", noBooks: "Nog geen boeke nie, genereer een!", read: "Lees", delete: "Verwyder", chapters: "{count} hoofstukke", confirmDelete: "Is jy seker jy wil hierdie boek skrap? Lêers sal ook verwyder word. Hierdie aksie kan nie ongedaan gemaak word nie.", confirmDeleteTitle: "Skrap Boek", saved: "Bergingplek opgedateer" },
  network: { title: "P2P Netwerk", myInfo: "My Node Info", userId: "GebruikerID", ip: "IP Adres", bookCount: "BoekAantal", nodes: "AanlynNodes", noNodes: "Geen ander aanlyn nodes nie", books: "Gedeelde Boeke", noBooks: "Geen gedeelde boeke nie", download: "Laai Af", downloading: "Laai Af...", downloadSuccess: "Boek suksesvol afgelaai!", downloadFailed: "Aflaai misluk", confirmDownload: "Wil jy hierdie boek aflaai?", local: "Lokaal", p2p: "P2P", shareTab: "Deel", connectTab: "Koppel", redeemTab: "Ontvang", createShare: "Skep Deel Skakel", selectBook: "Kies Boek", allBooks: "Alle Boeke", expireTime: "Vervaldatum", hour: "uur", hours: "ure", days: "dae", generateLink: "Genereer Skakel", myShareLinks: "My Deel Skakels", noShareLinks: "Nog geen deel skakels nie", copy: "Kopieer", expiresAt: "Verval om", connectPeer: "Koppel aan Peers", peerAddress: "Peer Adres", peerPort: "Poort", connecting: "Koppel...", connect: "Koppel", connected: "Gekoppel", connectFailed: "Koppeling misluk", peerBooks: "Peer Boeke", redeemShare: "Ontvang via Deel Skakel", redeemHelpDesc: "Plak die deel skakel of token om boeke te ontvang", shareToken: "Deel Token", peerHost: "Peer Gasheer", redeemBtn: "Ontvang Boek", redeemFailed: "Ontvang misluk", shareCreated: "Deel skakel geskep", shareHelpTitle: "Hoe om Deel Skakels te Gebruik", shareHelpDesc: "Stuur die genereer skakel aan jou peer. Hulle kan dit in die 'Ontvang' oortjie plak om jou boeke te kry." },
  reader: { loading: "Laai...", notFound: "Boek nie gevind nie", back: "Terug na Bibliotheek" },
  modal: { confirm: "Bevestig", cancel: "Kanselleer" }
};

// am — Amharic
translations.am = {
  nav: { generate: "አመንግድ", history: "ታሪክ", library: "መጻሕፍት", network: "ኔትዎርክ" },
  generate: { title: "የብራው መጽሐፍ አመንግድ", description: "መፍጠር የምትፈልገውን መጽሐፍ ገልጽ", placeholder: "ለምሳሌ፣ ለጀማሪዎች ስለ ሠራተኛ ብрагነት መግቢያ መጽሐፍ...", difficulty: "ርঠ", wordCount: "ተ奋斗目标 ቃላት", chapterCount: "የምዕራፎች ብዛት", style: "ዘይቤ", language: "የፍጪት ቋንቋ", start: "አመንግድ ጀምር", generating: "በማመንግድ ላይ...", cancel: "ሰርዝ", outlinePreview: "ንድፍ ቅድመ እይታ", progress: "የማመንግድ ሂደት", taskRunning: "ተግባር #{id} · ገጹን መቀየር ማመንግድን አይገልልም", completed: "ማመንግድ ተጠናቅቋል!", reconnecting: "በ 다시 መገናኘት ላይ...", reconnectFailed: "መገናኘት አልተሳካም", cancelled: "ተሰርቷል", error: "ስህተት", preparing: "በማዘጋጀት ላይ...", simple: "ቀላል", medium: "መካከለኛ", hard: "ከባድ" },
  history: { title: "የማመንግድ ታሪክ", newGenerate: "አዲስ ማመንግድ", all: "ሁሉም", pending: "በሂደት ውስጥ", completed: "ተጠናቅቋል", failed: "አልተሳካም", deleted: "ጠፍቷል", noRecords: "የታሪክ መዝገብ የለም", goGenerate: "የብራው መጽሐፍ አመንግድ", viewProgress: "ሂደት ይመልከቱ", cancel: "ሰርዝ", read: "አንብብ", regenerate: "እንደገና አመንግድ", delete: "ሰርዝ", createdAt: "ተፈጥሯል", completedAt: "ተጠናቅቋል", difficulty: "ርঠ", wordCount: "ተ奋斗目标 ቃላት", chapters: "ምዕራፎች", realtimeProgress: "በእውነተኛ ጊዜ ሂደት", processing: "በማቀድረስ ላይ...", chapter: "ምዕራፍ {current}", totalChapters: "ጠቅላላ {total} ምዕራፎች", outline: "ንድፍ", error: "ስህተት", confirmDelete: "ይህን መዝገብ መሰረዝ እርግጠኛ ነዎት? ይህ ተግባር መቀየር አይችልም።", confirmDeleteTitle: "መዝገብ ሰርዝ" },
  library: { title: "የእኔ መጻሕፍት", settings: "ቅንብሮች", userInfo: "የተጠቃሚ መረጃ", userId: "የተጠቃሚ መለያ", booksDir: "የመጽሐፍ ማስቀመጫ ቦታ", save: "አስቀምጥ", currentDir: "የአሁን ቦታ", all: "ሁሉም", local: "የአካባቢ", p2p: "P2P ምንጭ", noBooks: "ምንም መጽሐፍ የለም፣ አንድ አመንግድ!", read: "አንብብ", delete: "ሰርዝ", chapters: "{count} ምዕራፎች", confirmDelete: "ይህን መጽሐፍ መሰረዝ እርግጠኛ ነዎት? የአካባቢ ፋይሎችም ይሰረዛሉ። ይህ ተግባር መቀየር አይችልም።", confirmDeleteTitle: "መጽሐፍ ሰርዝ", saved: "ማስቀመጫ ቦታ ተዘምኗል" },
  network: { title: "P2P ኔትዎርክ", myInfo: "የእኔ ማውlicit መረጃ", userId: "የተጠቃሚ መለያ", ip: "IP አድራሻ", bookCount: "የመጽሐፍ ብዛት", nodes: "መስመር ላይ ላሉ ማውlicit", noNodes: "ሌላ መስመር ላይ ማውlicit የለም", books: "የተጋራ መጻሕፍት", noBooks: "የተጋራ መጽሐፍ የለም", download: "አውርድ", downloading: "በማውረድ ላይ...", downloadSuccess: "መጽሐፍ በተሳካ ሁኔታ ተውርድ!", downloadFailed: "ማውረድ አልተሳካም", confirmDownload: "ይህን መጽሐፍ ማውረድ ይፈልጋሉ?", local: "የአካባቢ", p2p: "P2P", shareTab: "ያጋሩ", connectTab: "ያገናኙ", redeemTab: "ያግኙ", createShare: "የማጋራት ማስፈንጫ ፍጠር", selectBook: "መጽሐፍ ምረጥ", allBooks: "ሁሉም መጻሕፍት", expireTime: "ጊዜ ማብቅ", hour: "ሰዓት", hours: "ሰዓታት", days: "ቀናት", generateLink: "ማስፈንጫ ፍጠር", myShareLinks: "የእኔ የማጋራት ማስፈንጫ", noShareLinks: "ምንም የማጋራት ማስፈንጫ የለም", copy: "ቅዳ", expiresAt: "ማብቂያ ጊዜ", connectPeer: "ከመካከል ጋር ያገናኙ", peerAddress: "የመካከል አድራሻ", peerPort: "ፖርት", connecting: "በማገናኘት ላይ...", connect: "ያገናኙ", connected: "ተገናኗል", connectFailed: "ማገናኘት አልተሳካም", peerBooks: "የመካከል መጻሕፍት", redeemShare: "በማጋራት ማስፈንጫ ያግኙ", redeemHelpDesc: "መጻሕፍት ለማግኘት የማጋራት ማስፈንጫ ወይም ቼከን ያስቀምጡ", shareToken: "የማጋራት ቼከን", peerHost: "የመካከል አቀባሪ", redeemBtn: "መጽሐፍ ያግኙ", redeemFailed: "ማግኘት አልተሳካም", shareCreated: "የማጋራት ማስፈንጫ ተፈጥሯል", shareHelpTitle: "የማጋራት ማስፈንጫ እንዴት መጠቀም", shareHelpDesc: "የተፈጥረውን ማስፈንጫ ለመካከል ይላኩ። እነሱ መጻሕፍትን ለማግኘት በ'ያግኙ' በቅርብ ይስሩበታል።" },
  reader: { loading: "በማበርከት ላይ...", notFound: "መጽሐፍ አልተገኘም", back: "ወደ መጻሕፍት ተመለስ" },
  modal: { confirm: "ያረጋግጡ", cancel: "ሰርዝ" }
};

// az — Azerbaijani
translations.az = {
  nav: { generate: "Yarat", history: "Tarixçə", library: "Kitabxana", network: "Şəbəkə" },
  generate: { title: "eKitab Yarat", description: "Yaratmaq istədiyiniz kitabı təsvir edin", placeholder: "məs. Başlanğıc süni intellekt haqqında kitab...", difficulty: "Çətinlik", wordCount: "Hədəf söz sayı", chapterCount: "Fəsillər sayı", style: "Stil", language: "Çıxış dili", start: "Yaratmağa başla", generating: "Yaradılır...", cancel: "Ləğv et", outlinePreview: "Mövzu önizləmə", progress: "Yaratma irəliləyişi", taskRunning: "Tapşırıq #{id} · Səhifə dəyişmə yaratmanı dayandırmaz", completed: "Yaratma tamamlandı!", reconnecting: "Yenidən qoşulur...", reconnectFailed: "Yenidən qoşulma uğursuz", cancelled: "Ləğv edildi", error: "Xəta", preparing: "Hazırlanır...", simple: "Asan", medium: "Orta", hard: "Çətin" },
  history: { title: "Yaratma tarixçəsi", newGenerate: "Yeni yaratma", all: "Hamısı", pending: "Davam edir", completed: "Tamamlandı", failed: "Uğursuz", del
