# Beiträge (WordPress-Import) enthalten wurzel-relative Pfade wie "/assets/uploads/..." oder "/<slug>/",
# die nicht über relative_url laufen (render_with_liquid: false).
# Läuft die Seite unter einem Unterpfad (z. B. Vorschau auf github.io/StartupDorf/),
# wird hier die baseurl davorgesetzt. Mit eigener Domain (baseurl leer) passiert nichts.

# Bilder & Dateien: in allen Dokumenten und Seiten, beide Anführungszeichen-Arten, auch CSS url(…)
UPLOADS_PATTERN = %r{(=\s*["']|url\(\s*["']?)/assets/uploads/}

Jekyll::Hooks.register [:posts, :documents, :pages], :post_render do |doc|
  base = doc.site.config["baseurl"].to_s.chomp("/")
  next if base.empty? || doc.output.nil?
  doc.output = doc.output.gsub(UPLOADS_PATTERN) { "#{$1}#{base}/assets/uploads/" }
end

# Interne Links (href="/…") nur in Beiträgen: Layout-Teile nutzen relative_url und haben die
# baseurl schon. Deshalb alles überspringen, was bereits mit der baseurl oder mit "//" beginnt.
Jekyll::Hooks.register :posts, :post_render do |doc|
  base = doc.site.config["baseurl"].to_s.chomp("/")
  next if base.empty? || doc.output.nil?
  pattern = %r{(\bhref=["'])/(?!/|#{Regexp.escape(base.delete_prefix("/"))}(?:/|["']))}
  doc.output = doc.output.gsub(pattern) { "#{$1}#{base}/" }
end
