import { useTranslation } from 'react-i18next';
import CategoryView from '../components/CategoryView';
import { useDogFood } from '../lib/loadData';

export default function DogFood() {
  const { t } = useTranslation();
  const { data } = useDogFood();
  return (
    <CategoryView
      title={t('dogFood.title')}
      desc={t('dogFood.desc')}
      category="dog-food"
      data={data}
      fitPlatforms={['YouTube', 'TikTok', 'Instagram', 'Reddit']}
    />
  );
}
