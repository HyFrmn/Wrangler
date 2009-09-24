class CreateCattles < ActiveRecord::Migration
  def self.up
    create_table :cattles do |t|
      t.string :hostname
      t.float :memory
      t.string :system
      t.string :processor
      t.integer :ncpus
      t.boolean :enabled

      t.timestamps
    end
  end

  def self.down
    drop_table :cattles
  end
end
