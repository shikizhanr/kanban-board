import React from 'react';
import { IonCard, IonCardHeader, IonCardTitle, IonCardSubtitle, IonCardContent } from '@ionic/react';

interface ItemCardProps {
  title: string;
  subtitle?: string;
  content: string;
  onClick?: () => void;
}

const ItemCard: React.FC<ItemCardProps> = ({ title, subtitle, content, onClick }) => {
  return (
    <IonCard onClick={onClick} button={!!onClick}>
      <IonCardHeader>
        <IonCardTitle>{title}</IonCardTitle>
        {subtitle && <IonCardSubtitle>{subtitle}</IonCardSubtitle>}
      </IonCardHeader>
      <IonCardContent>
        {content}
      </IonCardContent>
    </IonCard>
  );
};

export default ItemCard;
