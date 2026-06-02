const items = ['TEF Programme','Bank of Industry','YouWiN Connect','NIRSAL Microfinance','SMEDAN Grants','CBN Facilities','AfDB Youth Fund','LSETF Lagos','WOTCLEF Women']

export default function Marquee() {
  const all = [...items, ...items]
  return (
    <div className="marquee-strip">
      <div className="marquee-track">
        {all.map((item, i) => (
          <span key={i} className="marquee-item">
            <svg width="5" height="5" viewBox="0 0 5 5"><circle cx="2.5" cy="2.5" r="2.5" fill="var(--green-vivid)"/></svg>
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}
