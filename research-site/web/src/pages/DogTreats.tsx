import { useTranslation } from 'react-i18next';
import CategoryView from '../components/CategoryView';
import { useDogTreats } from '../lib/loadData';

export default function DogTreats() {
  const { t } = useTranslation();
  const { data } = useDogTreats();
  return (
    <CategoryView
      title={t('dogTreats.title')}
      desc={t('dogTreats.desc')}
      category="dog-treats"
      data={data}
      fitPlatforms={['YouTube', 'TikTok', 'Instagram', 'Reddit']}
    />
  );
}
