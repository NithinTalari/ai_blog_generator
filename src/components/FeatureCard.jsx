function FeatureCard({ icon: Icon, title, description, accent }) {
  return (
    <div className="glass-card rounded-[22px] p-6 transition duration-300 hover:-translate-y-1 hover:border-white/[0.14]">
      <div className={`mb-5 flex h-11 w-11 items-center justify-center rounded-xl ${accent}`}>
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mb-3 text-lg font-semibold text-white">{title}</h3>
      <p className="text-sm leading-6 text-white/60">{description}</p>
    </div>
  );
}

export default FeatureCard;
