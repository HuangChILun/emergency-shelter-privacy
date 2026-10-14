# 靜態網站維護

網站直接由根目錄 HTML 與 `assets/` 提供內容，部署沿用既有 GitHub Pages workflow。文章正文與內部連結不依賴 JavaScript；`assets/checklist.js` 僅提供勾選進度、複製與列印。

修改首頁 Tailwind class 後重新產生並提交 CSS：

```sh
npm ci
npm run build:css
npm run check
```

其他指南共用 `assets/guides.css`。Lucide 固定為 0.475.0，授權保留於 `assets/lucide-LICENSE.txt`。不需在部署時安裝套件。

內容更新時，核對官方來源、可見查核日期、Article 的 `dateModified` 與 sitemap 的 `lastmod`；不要僅為 SEO 改日期。新增頁面需設定唯一 title／description、自指 canonical、結構化資料，並從首頁或指南入口放入可爬取連結，再更新 sitemap。

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

於瀏覽器開啟 `http://127.0.0.1:8765/`，確認手機與桌面排版、導覽與 FAQ；清單需確認勾選、重新整理後保留、複製與重設。無法使用本機儲存時仍應可閱讀完整清單。

SEO 成效以 Search Console 比較上線後與前期的非品牌曝光、點擊、CTR、各落地頁與查詢字詞。sitemap 收到不代表已索引；新增頁面由 Google 決定抓取與收錄時間。
